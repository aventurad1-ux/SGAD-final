
import pyotp

from app.services.totp_service import (
    generar_secreto_totp,
    generar_uri_totp,
    verificar_codigo_totp,
)


def test_generar_secreto():
    secreto = generar_secreto_totp()

    assert isinstance(secreto, str)
    assert len(secreto) >= 32


def test_generar_uri():
    secreto = generar_secreto_totp()

    uri = generar_uri_totp(
        secreto,
        "prueba@sgad.local"
    )

    assert uri.startswith("otpauth://totp/")
    assert "SGAD" in uri


def test_aceptar_codigo_correcto():
    secreto = generar_secreto_totp()
    codigo = pyotp.TOTP(secreto).now()

    assert verificar_codigo_totp(
        secreto,
        codigo
    ) is True


def test_rechazar_codigo_incorrecto():
    secreto = generar_secreto_totp()

    assert verificar_codigo_totp(
        secreto,
        "abcdef"
    ) is False

    assert verificar_codigo_totp(
        secreto,
        "123"
    ) is False


def test_rechazar_codigo_vencido():
    secreto = generar_secreto_totp()
    totp = pyotp.TOTP(secreto)

    # Código generado hace dos minutos.
    codigo_vencido = totp.at(
        totp.timecode(
            __import__("datetime").datetime.now()
        ) * 30 - 120
    )

    assert verificar_codigo_totp(
        secreto,
        codigo_vencido
    ) is False
