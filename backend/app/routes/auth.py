
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    get_jwt_identity,
    jwt_required
)

from app.extensions import db
from app.models.usuario import Usuario
from app.models.refresh_token import RefreshToken
from app.services.password_service import verify_password
from app.services.bitacora_service import registrar_actividad


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    correo = data.get("correo", "").strip().lower()
    password = data.get("password", "")

    if not correo or not password:
        return jsonify({
            "message": "Correo y contraseña son obligatorios."
        }), 400

    usuario = Usuario.query.filter_by(
        correo=correo
    ).first()

    if not usuario:
        return jsonify({
            "message": "Credenciales incorrectas."
        }), 401

    if not usuario.activo:
        return jsonify({
            "message": "La cuenta se encuentra desactivada."
        }), 403

    if not verify_password(
        usuario.contrasena_hash,
        password
    ):
        return jsonify({
            "message": "Credenciales incorrectas."
        }), 401

    claims = {
        "rol": usuario.rol.nombre
    }

    access_token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims=claims
    )

    refresh_token = create_refresh_token(
        identity=str(usuario.id_usuario),
        additional_claims=claims
    )

    refresh_data = decode_token(refresh_token)

    token_db = RefreshToken(
        id_usuario=usuario.id_usuario,
        jti=refresh_data["jti"],
        fecha_expiracion=datetime.fromtimestamp(
            refresh_data["exp"],
            tz=timezone.utc
        ),
        direccion_ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent")
    )

    db.session.add(token_db)

    registrar_actividad(
        id_usuario=usuario.id_usuario,
        accion="INICIAR_SESION",
        modulo="Autenticacion",
        descripcion="El usuario inicio sesion correctamente."
    )

    db.session.commit()

    return jsonify({
        "message": "Inicio de sesión exitoso.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre
        }
    }), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    usuario_id = int(get_jwt_identity())
    jwt_data = get_jwt()
    jti = jwt_data["jti"]

    token_db = RefreshToken.query.filter_by(
        jti=jti,
        revocado=False
    ).first()

    if not token_db:
        return jsonify({
            "message": "Refresh token inválido o revocado."
        }), 401

    usuario = db.session.get(Usuario, usuario_id)

    if not usuario or not usuario.activo:
        return jsonify({
            "message": "Usuario no disponible."
        }), 401

    claims = {
        "rol": usuario.rol.nombre
    }

    nuevo_access_token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims=claims
    )

    return jsonify({
        "access_token": nuevo_access_token
    }), 200


@auth_bp.post("/logout")
@jwt_required(refresh=True)
def logout():
    jwt_data = get_jwt()
    jti = jwt_data["jti"]

    token_db = RefreshToken.query.filter_by(
        jti=jti
    ).first()

    if token_db:
        token_db.revocado = True
        token_db.fecha_revocacion = datetime.now(timezone.utc)

        db.session.commit()

    return jsonify({
        "message": "Sesión cerrada correctamente."
    }), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    usuario_id = int(get_jwt_identity())

    usuario = db.session.get(Usuario, usuario_id)

    if not usuario:
        return jsonify({
            "message": "Usuario no encontrado."
        }), 404

    return jsonify({
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre
        }
    }), 200
