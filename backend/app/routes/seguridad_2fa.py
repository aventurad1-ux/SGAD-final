from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.recuperacion_2fa_service import (
    consumir_codigo_recuperacion,
)

from app.models.refresh_token import RefreshToken
from app.services.bitacora_service import registrar_actividad
from datetime import datetime, timedelta, timezone
import hmac
import time

import pyotp
from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models.usuario import Usuario
from app.models.usuario_2fa import Usuario2FA
from app.models.codigo_recuperacion_2fa import CodigoRecuperacion2FA
from app.services.desafio_2fa import validar_desafio_2fa
from app.services.totp_service import (
    generar_secreto_totp,
    generar_uri_totp,
)
from app.services.cifrado_2fa import (
    cifrar_secreto_totp,
    descifrar_secreto_totp,
)
from app.services.codigos_recuperacion import (
    generar_codigos_recuperacion,
    generar_hash_codigo,
)


seguridad_2fa_bp = Blueprint(
    "seguridad_2fa",
    __name__,
    url_prefix="/api/auth/2fa",
)


def obtener_usuario_del_desafio():
    data = request.get_json(silent=True) or {}
    id_usuario = validar_desafio_2fa(
        data.get("desafio")
    )

    if not id_usuario:
        return None, data

    usuario = db.session.get(Usuario, id_usuario)

    if not usuario or not usuario.activo:
        return None, data

    return usuario, data


def comprobar_totp(configuracion, codigo):
    if not isinstance(codigo, str):
        return False

    if len(codigo) != 6 or not codigo.isdigit():
        return False

    secreto = descifrar_secreto_totp(
        configuracion.secreto_cifrado
    )

    totp = pyotp.TOTP(secreto)
    paso_actual = int(time.time()) // 30

    for paso in range(paso_actual - 1, paso_actual + 2):
        if configuracion.ultimo_paso_usado is not None:
            if paso <= configuracion.ultimo_paso_usado:
                continue

        esperado = totp.at(paso * 30)

        if hmac.compare_digest(esperado, codigo):
            configuracion.ultimo_paso_usado = paso
            return True

    return False


def bloqueado(configuracion):
    if not configuracion.bloqueado_hasta:
        return False

    hasta = configuracion.bloqueado_hasta

    if hasta.tzinfo is None:
        hasta = hasta.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) < hasta


def registrar_fallo(configuracion):
    configuracion.intentos_fallidos += 1

    if configuracion.intentos_fallidos >= 5:
        configuracion.bloqueado_hasta = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        )
        configuracion.intentos_fallidos = 0

    db.session.commit()


@seguridad_2fa_bp.post("/setup")
def preparar_2fa():
    usuario, _ = obtener_usuario_del_desafio()

    if not usuario:
        return jsonify({
            "message": "Desafio invalido o vencido."
        }), 401

    configuracion = db.session.get(
        Usuario2FA, usuario.id_usuario
    )

    if configuracion and configuracion.habilitado:
        return jsonify({
            "message": "El segundo factor ya esta activado."
        }), 409

    # Si el usuario vuelve a solicitar el QR,
    # conservamos el mismo secreto pendiente.
    if not configuracion:
        configuracion = Usuario2FA(
            id_usuario=usuario.id_usuario,
            secreto_cifrado=cifrar_secreto_totp(
                generar_secreto_totp()
            ),
            habilitado=False,
            intentos_fallidos=0,
        )

        db.session.add(configuracion)
        db.session.commit()

    if bloqueado(configuracion):
        return jsonify({
            "message": "Demasiados intentos. Intente mas tarde."
        }), 429

    secreto = descifrar_secreto_totp(
        configuracion.secreto_cifrado
    )

    return jsonify({
        "message": "Configure Google Authenticator.",
        "provisioning_uri": generar_uri_totp(
            secreto, usuario.correo
        ),
    }), 200


@seguridad_2fa_bp.post("/activate")
def activar_2fa():
    usuario, data = obtener_usuario_del_desafio()

    if not usuario:
        return jsonify({
            "message": "Desafio invalido o vencido."
        }), 401

    configuracion = db.session.get(
        Usuario2FA, usuario.id_usuario
    )

    if not configuracion:
        return jsonify({
            "message": "Primero debe configurar el 2FA."
        }), 400

    if configuracion.habilitado:
        return jsonify({
            "message": "El 2FA ya fue activado."
        }), 409

    if bloqueado(configuracion):
        return jsonify({
            "message": "Demasiados intentos. Intente mas tarde."
        }), 429

    codigo = data.get("codigo", "")

    if not comprobar_totp(configuracion, codigo):
        registrar_fallo(configuracion)
        return jsonify({
            "message": "Codigo incorrecto o vencido."
        }), 401

    codigos = generar_codigos_recuperacion()

    for codigo_recuperacion in codigos:
        db.session.add(
            CodigoRecuperacion2FA(
                id_usuario=usuario.id_usuario,
                codigo_hash=generar_hash_codigo(
                    codigo_recuperacion
                ),
                utilizado=False,
            )
        )

    configuracion.habilitado = True
    configuracion.fecha_activacion = (
        datetime.now(timezone.utc)
    )
    configuracion.intentos_fallidos = 0
    configuracion.bloqueado_hasta = None

    db.session.commit()

    return jsonify({
        "message": "Google Authenticator activado.",
        "codigos_recuperacion": codigos,
    }), 200


@seguridad_2fa_bp.post("/verify")
def verificar_2fa():
    usuario, data = obtener_usuario_del_desafio()

    if not usuario:
        return jsonify({
            "message": "Desafio invalido o vencido."
        }), 401

    codigo = str(data.get("codigo") or "").strip()

    # Bloqueamos la fila durante la comprobacion
    # para evitar reutilizacion simultanea del TOTP.
    configuracion = (
        db.session.query(Usuario2FA)
        .filter_by(id_usuario=usuario.id_usuario)
        .with_for_update()
        .first()
    )

    if not configuracion or not configuracion.habilitado:
        db.session.rollback()
        return jsonify({
            "message": "Primero debe activar Google Authenticator."
        }), 403

    if bloqueado(configuracion):
        db.session.rollback()
        return jsonify({
            "message": "Demasiados intentos. Intente mas tarde."
        }), 429

    if not comprobar_totp(configuracion, codigo):
        registrar_fallo(configuracion)

        return jsonify({
            "message": "Codigo incorrecto o vencido."
        }), 401

    configuracion.intentos_fallidos = 0
    configuracion.bloqueado_hasta = None


    # Primero generamos el refresh token.
    # Su JTI identificara la sesion en PostgreSQL.
    refresh_token = create_refresh_token(
        identity=str(usuario.id_usuario),
        additional_claims={
            "rol": usuario.rol.nombre,
            "mfa": True,
        },
    )

    refresh_data = decode_token(refresh_token)
    id_sesion = refresh_data["jti"]

    # El access token queda vinculado a la misma sesion.
    access_token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims={
            "rol": usuario.rol.nombre,
            "mfa": True,
            "sid": id_sesion,
        },
    )


    token_db = RefreshToken(
        id_usuario=usuario.id_usuario,
        jti=refresh_data["jti"],
        fecha_expiracion=datetime.fromtimestamp(
            refresh_data["exp"],
            tz=timezone.utc,
        ),
        ultima_actividad=datetime.now(timezone.utc),
        direccion_ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )

    db.session.add(token_db)

    registrar_actividad(
        id_usuario=usuario.id_usuario,
        accion="INICIAR_SESION",
        modulo="Autenticacion",
        descripcion="Inicio de sesion con 2FA verificado.",
    )

    db.session.commit()

    return jsonify({
        "message": "Inicio de sesion exitoso.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre,
        },
    }), 200


@seguridad_2fa_bp.post("/recovery")
def recuperar_acceso_2fa():
    usuario, data = obtener_usuario_del_desafio()

    if not usuario:
        return jsonify({
            "message": "Desafio invalido o vencido."
        }), 401

    configuracion = (
        db.session.query(Usuario2FA)
        .filter_by(id_usuario=usuario.id_usuario)
        .with_for_update()
        .first()
    )

    if not configuracion or not configuracion.habilitado:
        db.session.rollback()
        return jsonify({
            "message": "El 2FA no esta activado."
        }), 403

    if bloqueado(configuracion):
        db.session.rollback()
        return jsonify({
            "message": "Demasiados intentos. Intente mas tarde."
        }), 429

    codigo = data.get("codigo", "")

    if not consumir_codigo_recuperacion(
        usuario.id_usuario, codigo
    ):
        registrar_fallo(configuracion)
        return jsonify({
            "message": "Codigo de recuperacion invalido o utilizado."
        }), 401

    configuracion.intentos_fallidos = 0
    configuracion.bloqueado_hasta = None

    refresh_token = create_refresh_token(
        identity=str(usuario.id_usuario),
        additional_claims={
            "rol": usuario.rol.nombre,
            "mfa": True,
        },
    )

    refresh_data = decode_token(refresh_token)
    id_sesion = refresh_data["jti"]

    access_token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims={
            "rol": usuario.rol.nombre,
            "mfa": True,
            "sid": id_sesion,
        },
    )

    db.session.add(
        RefreshToken(
            id_usuario=usuario.id_usuario,
            jti=id_sesion,
            fecha_expiracion=datetime.fromtimestamp(
                refresh_data["exp"],
                tz=timezone.utc,
            ),
            ultima_actividad=datetime.now(timezone.utc),
            direccion_ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
    )

    registrar_actividad(
        id_usuario=usuario.id_usuario,
        accion="INICIAR_SESION",
        modulo="Autenticacion",
        descripcion="Acceso con codigo de recuperacion 2FA.",
    )

    db.session.commit()

    return jsonify({
        "message": "Acceso recuperado correctamente.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre,
        },
    }), 200


@seguridad_2fa_bp.post("/recovery-codes/regenerate")
@jwt_required()
def regenerar_codigos_2fa():
    id_usuario = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    codigo = str(data.get("codigo") or "").strip()

    if len(codigo) != 6 or not codigo.isdigit():
        return jsonify({
            "message": "Ingrese el codigo de Google Authenticator."
        }), 400

    configuracion = (
        db.session.query(Usuario2FA)
        .filter_by(id_usuario=id_usuario)
        .with_for_update()
        .first()
    )

    if not configuracion or not configuracion.habilitado:
        db.session.rollback()
        return jsonify({
            "message": "Google Authenticator no esta activado."
        }), 403

    if bloqueado(configuracion):
        db.session.rollback()
        return jsonify({
            "message": "Demasiados intentos. Intente mas tarde."
        }), 429

    if not comprobar_totp(configuracion, codigo):
        registrar_fallo(configuracion)
        return jsonify({
            "message": "Codigo incorrecto, vencido o utilizado."
        }), 401

    nuevos_codigos = generar_codigos_recuperacion()

    # Anular todos los codigos anteriores.
    CodigoRecuperacion2FA.query.filter_by(
        id_usuario=id_usuario
    ).delete(synchronize_session=False)

    # Guardar solamente los hashes de los nuevos.
    for item in nuevos_codigos:
        db.session.add(
            CodigoRecuperacion2FA(
                id_usuario=id_usuario,
                codigo_hash=generar_hash_codigo(item),
                utilizado=False
            )
        )

    configuracion.intentos_fallidos = 0
    configuracion.bloqueado_hasta = None

    db.session.commit()

    return jsonify({
        "message": "Codigos regenerados correctamente.",
        "codigos_recuperacion": nuevos_codigos
    }), 200
