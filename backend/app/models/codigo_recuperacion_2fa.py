
from datetime import datetime, timezone

from app.extensions import db


class CodigoRecuperacion2FA(db.Model):
    __tablename__ = "codigos_recuperacion_2fa"

    id_codigo = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios_2fa.id_usuario",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    codigo_hash = db.Column(
        db.String(64),
        nullable=False,
        unique=True
    )

    utilizado = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    fecha_creacion = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    fecha_uso = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )
