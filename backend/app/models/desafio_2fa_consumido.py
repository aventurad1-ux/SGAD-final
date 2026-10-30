
from datetime import datetime, timezone

from app.extensions import db


class Desafio2FAConsumido(db.Model):
    __tablename__ = "desafios_2fa_consumidos"

    token_hash = db.Column(
        db.String(64),
        primary_key=True
    )

    fecha_consumo = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
