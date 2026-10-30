import hashlib
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


HIBP_RANGE_URL = (
    "https://api.pwnedpasswords.com/range/{}"
)

TIMEOUT_SEGUNDOS = 8


class HIBPServiceError(Exception):
    """Error al consultar Pwned Passwords."""


def verificar_password_comprometida(password):
    """
    Consulta Have I Been Pwned usando k-anonimato.

    Nunca envía la contraseña completa ni su hash completo.

    Retorna:
        {
            "comprometida": bool,
            "apariciones": int
        }
    """

    if not password:
        return {
            "comprometida": False,
            "apariciones": 0,
        }

    # SHA-1 requerido por Pwned Passwords.
    hash_completo = (
        hashlib.sha1(
            password.encode("utf-8")
        )
        .hexdigest()
        .upper()
    )

    prefijo = hash_completo[:5]
    sufijo_buscado = hash_completo[5:]

    url = HIBP_RANGE_URL.format(
        prefijo
    )

    request = Request(
        url,
        headers={
            "User-Agent":
                "SGAD-Orfelinda/1.0",

            # Devuelve una cantidad uniforme
            # de resultados para reforzar
            # privacidad del rango consultado.
            "Add-Padding":
                "true",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=TIMEOUT_SEGUNDOS,
        ) as respuesta:
            contenido = (
                respuesta
                .read()
                .decode("utf-8")
            )

    except (
        HTTPError,
        URLError,
        TimeoutError,
    ) as error:
        raise HIBPServiceError(
            "No fue posible consultar "
            "Have I Been Pwned."
        ) from error

    for linea in contenido.splitlines():
        if ":" not in linea:
            continue

        sufijo, cantidad = (
            linea
            .strip()
            .split(":", 1)
        )

        if (
            sufijo.upper()
            == sufijo_buscado
        ):
            try:
                apariciones = int(
                    cantidad
                )
            except ValueError:
                apariciones = 0

            return {
                "comprometida": True,
                "apariciones": apariciones,
            }

    return {
        "comprometida": False,
        "apariciones": 0,
    }