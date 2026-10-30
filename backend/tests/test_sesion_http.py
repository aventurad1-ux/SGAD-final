
from datetime import datetime, timedelta, timezone

from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.refresh_token import RefreshToken


def test_rechazar_sesion_inactiva():
    app = create_app()

    with app.app_context():
        usuario = Usuario.query.filter_by(
            correo="directora@sgad.demo"
        ).first()

        assert usuario is not None, (
            "No existe la cuenta de prueba de directora."
        )

        ahora = datetime.now(timezone.utc)

        # JTI exclusivo para esta prueba.
        import uuid
        jti = str(uuid.uuid4())

        sesion = RefreshToken(
            id_usuario=usuario.id_usuario,
            jti=jti,
            fecha_expiracion=ahora + timedelta(hours=1),
            ultima_actividad=ahora - timedelta(minutes=31),
            revocado=False,
        )

        db.session.add(sesion)
        db.session.commit()

        try:
            token = create_access_token(
                identity=str(usuario.id_usuario),
                additional_claims={
                    "rol": usuario.rol.nombre,
                    "mfa": True,
                    "sid": jti,
                },
            )

            cliente = app.test_client()

            respuesta = cliente.get(
                "/api/auth/me",
                headers={
                    "Authorization": f"Bearer {token}"
                },
            )

            assert respuesta.status_code == 401, (
                f"Se esperaba 401, pero devolvio "
                f"{respuesta.status_code}: "
                f"{respuesta.get_json()}"
            )
        finally:
            db.session.delete(sesion)
            db.session.commit()
