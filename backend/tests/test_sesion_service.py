
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.sesion_service import sesion_vigente


def crear_sesion(minutos_inactiva=0, revocada=False):
    ahora = datetime.now(timezone.utc)

    return SimpleNamespace(
        revocado=revocada,
        fecha_expiracion=ahora + timedelta(days=1),
        ultima_actividad=ahora - timedelta(
            minutes=minutos_inactiva
        )
    )


def test_sesion_reciente():
    assert sesion_vigente(crear_sesion(5))


def test_sesion_inactiva():
    assert not sesion_vigente(crear_sesion(31))


def test_sesion_revocada():
    assert not sesion_vigente(
        crear_sesion(5, revocada=True)
    )


def test_sesion_sin_actividad():
    sesion = crear_sesion()
    sesion.ultima_actividad = None

    assert not sesion_vigente(sesion)


def test_sesion_expirada():
    sesion = crear_sesion()
    sesion.fecha_expiracion = (
        datetime.now(timezone.utc)
        - timedelta(minutes=1)
    )

    assert not sesion_vigente(sesion)
