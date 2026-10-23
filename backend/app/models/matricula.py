from app.extensions import db


class Matricula(db.Model):
    __tablename__ = "matriculas"

    id_matricula = db.Column(
        db.Integer,
        primary_key=True
    )

    id_estudiante = db.Column(
        db.Integer,
        db.ForeignKey(
            "estudiantes.id_estudiante",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    id_ciclo = db.Column(
        db.Integer,
        db.ForeignKey(
            "ciclos_escolares.id_ciclo",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    id_seccion = db.Column(
        db.Integer,
        db.ForeignKey(
            "secciones.id_seccion",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="Activa",
        server_default="Activa"
    )

    fecha_matricula = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    estudiante = db.relationship(
        "Estudiante",
        back_populates="matriculas",
        lazy="joined"
    )

    seccion = db.relationship(
        "Seccion",
        back_populates="matriculas",
        lazy="joined"
    )

    ciclo = db.relationship(
        "CicloEscolar",
        lazy="joined"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_estudiante",
            "id_ciclo",
            name="uq_matricula_estudiante_ciclo"
        ),
        db.CheckConstraint(
            "estado IN ('Activa', 'Retirada')",
            name="chk_matricula_estado"
        ),
    )