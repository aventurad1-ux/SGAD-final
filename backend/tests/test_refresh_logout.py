
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.refresh_token import RefreshToken


def crear_sesion_prueba(usuario, minutos_inactiva=0):
    ahora = datetime.now(timezone.utc)

    refresh_token = create_refresh_token(
        identity=str(usuario.id_usuario),
        additional_claims={
            "rol": usuario.rol.nombre,
            "mfa": True,
        },
    )

    jti = decode_token(refresh_token)["jti"]

    sesion = RefreshToken(
        id_usuario=usuario.id_usuario,
        jti=jti,
        fecha_expiracion=ahora + timedelta(hours=1),
        ultima_actividad=ahora - timedelta(
            minutes=minutos_inactiva
        ),
        revocado=False,
    )

    db.session.add(sesion)
    db.session.commit()

    return sesion, refresh_token


def test_refresh_rechaza_sesion_inactiva():
    app = create_app()

    with app.app_context():
        usuario = Usuario.query.filter_by(
            correo="directora@sgad.demo"
        ).first()

        assert usuario is not None

        sesion, refresh_token = crear_sesion_prueba(
            usuario,
            minutos_inactiva=31,
        )

        try:
            respuesta = app.test_client().post(
                "/api/auth/refresh",
                headers={
                    "Authorization": f"Bearer {refresh_token}"
                },
            )

            assert respuesta.status_code == 401
        finally:
            db.session.delete(sesion)
            db.session.commit()


def test_logout_revoca_sesion():
    app = create_app()

    with app.app_context():
        usuario = Usuario.query.filter_by(
            correo="directora@sgad.demo"
        ).first()

        assert usuario is not None

        sesion, refresh_token = crear_sesion_prueba(
            usuario
        )

        try:
            respuesta = app.test_client().post(
                "/api/auth/logout",
                headers={
                    "Authorization": f"Bearer {refresh_token}"
                },
            )

            assert respuesta.status_code == 200

            db.session.refresh(sesion)
            assert sesion.revocado is True

            # Una vez cerrada la sesion, refresh debe fallar.
            segunda = app.test_client().post(
                "/api/auth/refresh",
                headers={
                    "Authorization": f"Bearer {refresh_token}"
                },
            )

            assert segunda.status_code == 401
        finally:
            db.session.delete(sesion)
            db.session.commit()
