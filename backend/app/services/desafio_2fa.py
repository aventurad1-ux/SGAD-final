from sqlalchemy.dialects.postgresql import insert
import hashlib

from app.extensions import db
from app.models.desafio_2fa_consumido import Desafio2FAConsumido
import secrets

from flask import current_app
from itsdangerous import (
    URLSafeTimedSerializer,
    BadSignature,
    SignatureExpired,
)

DURACION_DESAFIO = 300  # 5 minutos


def obtener_firmador():
    clave = current_app.config.get("JWT_SECRET_KEY")

    if not clave:
        raise RuntimeError(
            "JWT_SECRET_KEY no configurada"
        )

    return URLSafeTimedSerializer(
        secret_key=clave,
        salt="sgad-autenticacion-2fa-v1",
    )


def crear_desafio_2fa(id_usuario):
    """Crea un desafio temporal unico para el usuario."""
    return obtener_firmador().dumps({
        "id_usuario": int(id_usuario),
        "proposito": "verificar_2fa",
        "nonce": secrets.token_urlsafe(24),
    })


def validar_desafio_2fa(token):
    """Valida la firma y el vencimiento del desafio."""
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



def consumir_desafio_2fa(token):
    """
    Consume un desafio una sola vez.
    PostgreSQL impide reutilizaciones simultaneas.
    """
    if validar_desafio_2fa(token) is None:
        return False

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    sentencia = (
        insert(Desafio2FAConsumido)
        .values(token_hash=token_hash)
        .on_conflict_do_nothing(
            index_elements=["token_hash"]
        )
        .returning(Desafio2FAConsumido.token_hash)
    )

    resultado = db.session.execute(
        sentencia
    ).scalar_one_or_none()

    return resultado is not None
