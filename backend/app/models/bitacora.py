from datetime import datetime

from app.extensions import db


class Bitacora(db.Model):
    __tablename__ = "bitacora"

    id_bitacora = db.Column(
        db.Integer,
        db.Identity(always=True),
        primary_key=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    accion = db.Column(
        db.String(100),
        nullable=False
    )

    modulo = db.Column(
        db.String(100),
        nullable=False
    )

    registro = db.Column(
        db.String(255),
        nullable=True
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    fecha_hora = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario"
    )

    def __repr__(self):
        return (
            f"<Bitacora id={self.id_bitacora} "
            f"accion={self.accion}>"
        )
