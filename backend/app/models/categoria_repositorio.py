from app.extensions import db


class CategoriaRepositorio(db.Model):
    __tablename__ = "categorias_repositorio"

    id_categoria = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    activa = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    documentos = db.relationship(
        "DocumentoInstitucional",
        back_populates="categoria",
        lazy=True
    )