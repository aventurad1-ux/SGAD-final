
import secrets
import hashlib
import hmac


def generar_codigos_recuperacion(cantidad=8):
    """Genera códigos aleatorios para recuperar el acceso."""
    return [
        secrets.token_hex(8).upper()
        for _ in range(cantidad)
    ]


def generar_hash_codigo(codigo):
    """Crea un hash del código para no guardarlo en texto plano."""
    codigo_normalizado = codigo.strip().upper()
    return hashlib.sha256(
        codigo_normalizado.encode("utf-8")
    ).hexdigest()


def verificar_codigo_recuperacion(codigo, hash_guardado):
    """Comprueba si un código coincide con su hash."""
    hash_ingresado = generar_hash_codigo(codigo)

    return hmac.compare_digest(
        hash_ingresado,
        hash_guardado
    )
