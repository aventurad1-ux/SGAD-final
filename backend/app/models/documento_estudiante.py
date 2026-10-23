from app.extensions import db


class DocumentoEstudiante(db.Model):
    __tablename__ = "documentos_estudiante"

    id_documento = db.Column(
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

    id_requisito = db.Column(
        db.Integer,
        db.ForeignKey(
            "requisitos_expediente.id_requisito",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    version_actual = db.Column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1"
    )

    estado = db.Column(
        db.String(30),
        nullable=False,
        default="Entregado",
        server_default="Entregado"
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    estudiante = db.relationship(
        "Estudiante",
        back_populates="documentos",
        lazy="joined"
    )

    requisito = db.relationship(
        "RequisitoExpediente",
        back_populates="documentos",
        lazy="joined"
    )

    versiones = db.relationship(
        "VersionDocumentoEstudiante",
        back_populates="documento",
        cascade="all, delete-orphan",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_estudiante",
            "id_ciclo",
            "id_requisito",
            name="uq_documento_estudiante_ciclo_requisito"
        ),
    )