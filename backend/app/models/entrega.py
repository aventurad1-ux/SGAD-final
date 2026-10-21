from app.extensions import db


class Entrega(db.Model):
    __tablename__ = "entregas"

    id_entrega = db.Column(
        db.Integer,
        primary_key=True
    )

    id_destinatario = db.Column(
        db.Integer,
        db.ForeignKey(
            "solicitud_destinatarios.id_destinatario",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    id_requisito_solicitud = db.Column(
        db.Integer,
        db.ForeignKey(
            "solicitud_requisitos.id_requisito_solicitud",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    estado = db.Column(
        db.String(25),
        nullable=False,
        default="pendiente",
        server_default="pendiente"
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    fecha_primera_entrega = db.Column(
        db.DateTime,
        nullable=True
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=True
    )

    destinatario = db.relationship(
        "SolicitudDestinatario",
        back_populates="entregas"
    )

    requisito = db.relationship(
        "SolicitudRequisito",
        back_populates="entregas"
    )

    versiones = db.relationship(
        "VersionEntrega",
        back_populates="entrega",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_destinatario",
            "id_requisito_solicitud",
            name="uq_entrega_destinatario_requisito"
        ),
        db.CheckConstraint(
            """
            estado IN (
                'pendiente',
                'entregado',
                'en_revision',
                'correccion_solicitada',
                'aprobado',
                'rechazado'
            )
            """,
            name="chk_entregas_estado"
        ),
        db.CheckConstraint(
            """
            estado = 'pendiente'
            OR fecha_primera_entrega IS NOT NULL
            """,
            name="chk_entregas_fecha"
        ),
    )