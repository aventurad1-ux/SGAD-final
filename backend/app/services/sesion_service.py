
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.refresh_token import RefreshToken


TIEMPO_INACTIVIDAD = timedelta(minutes=30)


def fecha_utc(fecha):
    """Normaliza fechas provenientes de PostgreSQL."""
    if fecha is None:
        return None

    if fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)

    return fecha.astimezone(timezone.utc)


def obtener_sesion(jti_sesion):
    """Busca una sesion registrada en PostgreSQL."""
    if not jti_sesion:
        return None

    return RefreshToken.query.filter_by(
        jti=jti_sesion
    ).first()


def sesion_vigente(sesion):
    """Comprueba que no este revocada ni vencida."""
    if sesion is None or sesion.revocado:
        return False

    ahora = datetime.now(timezone.utc)

    vencimiento = fecha_utc(sesion.fecha_expiracion)
    ultima = fecha_utc(sesion.ultima_actividad)

    if not vencimiento or vencimiento <= ahora:
        return False

    # Sesiones antiguas sin seguimiento de actividad
    # no pueden continuar autenticadas.
    if ultima is None:
        return False

    if ahora - ultima >= TIEMPO_INACTIVIDAD:
        return False

    return True


def registrar_actividad_sesion(sesion):
    """Actualiza la actividad despues de validar la sesion."""
    if not sesion_vigente(sesion):
        return False

    sesion.ultima_actividad = datetime.now(timezone.utc)
    db.session.commit()

    return True


def revocar_sesion(sesion):
    """Invalida una sesion registrada."""
    if sesion is None:
        return False

    sesion.revocado = True
    sesion.fecha_revocacion = datetime.now(timezone.utc)

    db.session.commit()
    return True
