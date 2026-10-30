
from datetime import datetime, timezone

from app.extensions import db
from app.models.codigo_recuperacion_2fa import CodigoRecuperacion2FA
from app.services.codigos_recuperacion import generar_hash_codigo


def consumir_codigo_recuperacion(id_usuario, codigo):
    """Marca un código como usado dentro de la transacción actual.

    Devuelve True si lo encontró disponible.
    El llamador debe confirmar o revertir la transacción.
    """
    if not isinstance(codigo, str):
        return False

    codigo = codigo.strip().upper()

    if len(codigo) != 16:
        return False

    if any(c not in "0123456789ABCDEF" for c in codigo):
        return False

    codigo_hash = generar_hash_codigo(codigo)

    registro = (
        db.session.query(CodigoRecuperacion2FA)
        .filter_by(
            id_usuario=id_usuario,
            codigo_hash=codigo_hash,
            utilizado=False,
        )
        .with_for_update()
        .first()
    )

    if registro is None:
        return False

    registro.utilizado = True
    registro.fecha_uso = datetime.now(timezone.utc)

    db.session.flush()
    return True
