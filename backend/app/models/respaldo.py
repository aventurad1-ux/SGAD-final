from datetime import datetime

from app.extensions import db


class Respaldo(db.Model):
    __tablename__ = "respaldos"

    # Identificador del respaldo
    id_respaldo = db.Column(
        db.Integer,
        db.Identity(always=True),
        primary_key=True
    )

    # Usuario que generó el respaldo
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    # Nombre del archivo ZIP
    nombre_archivo = db.Column(
        db.String(255)
    )

    # Tipo de respaldo
    tipo = db.Column(
        db.String(50),
        nullable=False,
        default="Completo"
    )

    # Fecha y hora
    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Tamaño del archivo en bytes
    tamano = db.Column(
        db.BigInteger
    )

    # Estado del respaldo
    estado = db.Column(
        db.String(30),
        nullable=False,
        default="En proceso"
    )

    # Mensaje de error, si ocurre alguno
    mensaje_error = db.Column(
        db.Text
    )

    # Relación con el usuario responsable
    usuario = db.relationship(
        "Usuario"
    )

    def __repr__(self):
        return f"<Respaldo {self.id_respaldo} - {self.estado}>"