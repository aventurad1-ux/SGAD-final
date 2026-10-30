
import os

from cryptography.fernet import Fernet, InvalidToken


def obtener_cifrador():
    clave = os.getenv("TOTP_ENCRYPTION_KEY")

    if not clave:
        raise RuntimeError(
            "Falta configurar TOTP_ENCRYPTION_KEY."
        )

    return Fernet(clave.encode("utf-8"))


def cifrar_secreto_totp(secreto):
    return obtener_cifrador().encrypt(
        secreto.encode("utf-8")
    ).decode("utf-8")


def descifrar_secreto_totp(secreto_cifrado):
    return obtener_cifrador().decrypt(
        secreto_cifrado.encode("utf-8")
    ).decode("utf-8")
