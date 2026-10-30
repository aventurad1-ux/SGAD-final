
from flask import current_app
from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)


DURACION_DESAFIO = 300  # Cinco minutos


def obtener_firmador():
    clave = current_app.config.get("JWT_SECRET_KEY")

    if not clave:
        raise RuntimeError("JWT_SECRET_KEY no configurada")

    return URLSafeTimedSerializer(
        secret_key=clave,
        salt="sgad-autenticacion-2fa-v1",
    )


def crear_desafio_2fa(id_usuario):
    """Comprobante temporal: NO es un JWT de acceso."""
    firmador = obtener_firmador()

    return firmador.dumps({
        "id_usuario": int(id_usuario),
        "proposito": "verificar_2fa",
    })


def validar_desafio_2fa(token):
    """Devuelve el id del usuario si el desafío es válido."""
    if not token or not isinstance(token, str):
        return None

    try:
        datos = obtener_firmador().loads(
            token,
            max_age=DURACION_DESAFIO,
        )

        if datos.get("proposito") != "verificar_2fa":
            return None

        id_usuario = datos.get("id_usuario")

        if type(id_usuario) is not int or id_usuario <= 0:
            return None

        return id_usuario

    except (BadSignature, SignatureExpired, ValueError):
        return None
