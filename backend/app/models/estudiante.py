from app.extensions import db


class Estudiante(db.Model):
    __tablename__ = "estudiantes"

    id_estudiante = db.Column(
        db.Integer,
        primary_key=True
    )

    codigo = db.Column(
        db.String(30),
        nullable=False,
        unique=True
    )

    cui = db.Column(
        db.String(13),
        nullable=False,
        unique=True
    )

    nombres = db.Column(
        db.String(120),
        nullable=False
    )

    apellidos = db.Column(
        db.String(120),
        nullable=False
    )

    fecha_nacimiento = db.Column(
        db.Date,
        nullable=False
    )

    genero = db.Column(
        db.String(20),
        nullable=False
    )

    direccion = db.Column(
        db.String(255),
        nullable=False
    )

    encargado = db.Column(
        db.String(180),
        nullable=False
    )

    parentesco = db.Column(
        db.String(50),
        nullable=False
    )

    telefono = db.Column(
        db.String(8),
        nullable=False
    )

    activo = db.Column(
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

    matriculas = db.relationship(
        "Matricula",
        back_populates="estudiante",
        lazy=True
    )

    documentos = db.relationship(
        "DocumentoEstudiante",
        back_populates="estudiante",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "char_length(cui) = 13",
            name="chk_estudiante_cui"
        ),
        db.CheckConstraint(
            "char_length(telefono) = 8",
            name="chk_estudiante_telefono"
        ),
    )