
import pyotp


def generar_secreto_totp():
    """Genera un secreto para vincular una cuenta."""
    return pyotp.random_base32()


def generar_uri_totp(secreto, correo):
    """Genera la URI para Google Authenticator."""
    totp = pyotp.TOTP(secreto)

    return totp.provisioning_uri(
        name=correo,
        issuer_name="SGAD"
    )


def verificar_codigo_totp(secreto, codigo):
    """Verifica el código temporal de seis dígitos."""
    if not isinstance(codigo, str):
        return False

    if len(codigo) != 6 or not codigo.isdigit():
        return False

    try:
        totp = pyotp.TOTP(secreto)

        return totp.verify(
            codigo,
            valid_window=1
        )
    except (TypeError, ValueError):
        return False
