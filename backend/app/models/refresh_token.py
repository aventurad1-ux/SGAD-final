from datetime import datetime, timezone

from app.extensions import db


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id_refresh_token = db.Column(
        db.Integer,
        db.Identity(always=True),
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    jti = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    fecha_creacion = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    ultima_actividad = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        default=lambda: datetime.now(timezone.utc)
    )


    fecha_expiracion = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    revocado = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    fecha_revocacion = db.Column(
        db.DateTime(timezone=True)
    )

    direccion_ip = db.Column(
        db.String(45)
    )

    user_agent = db.Column(
        db.Text
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="refresh_tokens"
    )

    def __repr__(self):
        return (
            f"<RefreshToken usuario={self.id_usuario} "
            f"revocado={self.revocado}>"
        )