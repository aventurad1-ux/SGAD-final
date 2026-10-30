
from datetime import datetime, timezone

from app.extensions import db


class Usuario2FA(db.Model):
    __tablename__ = "usuarios_2fa"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    secreto_cifrado = db.Column(
        db.Text,
        nullable=False
    )

    habilitado = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    ultimo_paso_usado = db.Column(
        db.BigInteger,
        nullable=True
    )

    intentos_fallidos = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    bloqueado_hasta = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    fecha_activacion = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    fecha_creacion = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
