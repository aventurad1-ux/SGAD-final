from app.extensions import db


class SolicitudRequisito(db.Model):
    __tablename__ = "solicitud_requisitos"

    id_requisito_solicitud = db.Column(
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

    nombre_documento = db.Column(
        db.String(200),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    obligatorio = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true()
    )

    formato_permitido = db.Column(
        db.String(100),
        nullable=True
    )

    orden = db.Column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1"
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default=db.true()
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    solicitud = db.relationship(
        "Solicitud",
        back_populates="requisitos"
    )

    entregas = db.relationship(
        "Entrega",
        back_populates="requisito",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_solicitud",
            "nombre_documento",
            name="uq_solicitud_requisito_nombre"
        ),
        db.CheckConstraint(
            "orden > 0",
            name="chk_solicitud_requisito_orden"
        ),
        db.CheckConstraint(
            "LENGTH(TRIM(nombre_documento)) > 0",
            name="chk_solicitud_requisito_nombre"
        ),
    )