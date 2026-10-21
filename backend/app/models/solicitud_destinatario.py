from app.extensions import db


class SolicitudDestinatario(db.Model):
    __tablename__ = "solicitud_destinatarios"

    id_destinatario = db.Column(
        db.Integer,
        primary_key=True
    )

    id_solicitud = db.Column(
        db.Integer,
        db.ForeignKey(
            "solicitudes.id_solicitud",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    id_docente = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    fecha_asignacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    fecha_lectura = db.Column(
        db.DateTime,
        nullable=True
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="pendiente",
        server_default="pendiente"
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    solicitud = db.relationship(
        "Solicitud",
        back_populates="destinatarios"
    )

    docente = db.relationship(
        "Usuario",
        foreign_keys=[id_docente]
    )

    entregas = db.relationship(
        "Entrega",
        back_populates="destinatario",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_solicitud",
            "id_docente",
            name="uq_solicitud_docente"
        ),
        db.CheckConstraint(
            """
            estado IN (
                'pendiente',
                'en_proceso',
                'entregado',
                'cancelado'
            )
            """,
            name="chk_destinatarios_estado"
        ),
        db.CheckConstraint(
            """
            fecha_lectura IS NULL
            OR fecha_lectura >= fecha_asignacion
            """,
            name="chk_destinatarios_lectura"
        ),
    )