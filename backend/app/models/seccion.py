from app.extensions import db


class Seccion(db.Model):
    __tablename__ = "secciones"

    id_seccion = db.Column(
        db.Integer,
        primary_key=True
    )

    id_ciclo = db.Column(
        db.Integer,
        db.ForeignKey(
            "ciclos_escolares.id_ciclo",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    grado = db.Column(
        db.Integer,
        nullable=False
    )

    nombre = db.Column(
        db.String(20),
        nullable=False
    )

    id_docente = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="SET NULL"
        ),
        nullable=True
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

    ciclo = db.relationship(
        "CicloEscolar",
        lazy="joined"
    )

    docente = db.relationship(
        "Usuario",
        foreign_keys=[id_docente],
        lazy="joined"
    )

    matriculas = db.relationship(
        "Matricula",
        back_populates="seccion",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_ciclo",
            "grado",
            "nombre",
            name="uq_seccion_ciclo_grado_nombre"
        ),
        db.CheckConstraint(
            "grado BETWEEN 1 AND 6",
            name="chk_seccion_grado"
        ),
    )

    @property
    def etiqueta(self):
        return f"{self.grado}° {self.nombre}"