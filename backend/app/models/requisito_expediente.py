from app.extensions import db


class RequisitoExpediente(db.Model):
    __tablename__ = "requisitos_expediente"

    id_requisito = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    descripcion = db.Column(
        db.String(255),
        nullable=True
    )

    obligatorio = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    orden = db.Column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1"
    )

    documentos = db.relationship(
        "DocumentoEstudiante",
        back_populates="requisito",
        lazy=True
    )