from datetime import datetime, timezone

from app.extensions import db


class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id_notificacion = db.Column(
        db.Integer,
        primary_key=True,
    )

    id_usuario = db.Column(
        db.Integer,
        nullable=False,
        index=True,
    )

    id_ciclo = db.Column(
        db.Integer,
        nullable=True,
        index=True,
    )

    tipo = db.Column(
        db.String(50),
        nullable=False,
    )

    titulo = db.Column(
        db.String(180),
        nullable=False,
    )

    mensaje = db.Column(
        db.String(500),
        nullable=False,
    )

    ruta = db.Column(
        db.String(255),
        nullable=True,
    )

    id_referencia = db.Column(
        db.Integer,
        nullable=True,
    )

    referencia_tipo = db.Column(
        db.String(50),
        nullable=True,
    )

    leida = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    fecha_creacion = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
    )

    fecha_lectura = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    def to_dict(self):
        return {
            "id_notificacion":
                self.id_notificacion,

            "id_usuario":
                self.id_usuario,

            "id_ciclo":
                self.id_ciclo,

            "tipo":
                self.tipo,

            "titulo":
                self.titulo,

            "mensaje":
                self.mensaje,

            "ruta":
                self.ruta,

            "id_referencia":
                self.id_referencia,

            "referencia_tipo":
                self.referencia_tipo,

            "leida":
                self.leida,

            "fecha_creacion": (
                self.fecha_creacion.isoformat()
                if self.fecha_creacion
                else None
            ),

            "fecha_lectura": (
                self.fecha_lectura.isoformat()
                if self.fecha_lectura
                else None
            ),
        }