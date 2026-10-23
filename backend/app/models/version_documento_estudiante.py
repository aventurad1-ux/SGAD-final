from app.extensions import db


class VersionDocumentoEstudiante(db.Model):
    __tablename__ = "versiones_documento_estudiante"

    id_version = db.Column(
        db.Integer,
        primary_key=True
    )

    id_documento = db.Column(
        db.Integer,
        db.ForeignKey(
            "documentos_estudiante.id_documento",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    numero_version = db.Column(
        db.Integer,
        nullable=False
    )

    nombre_archivo = db.Column(
        db.String(255),
        nullable=False
    )

    ruta_archivo = db.Column(
        db.String(500),
        nullable=False,
        unique=True
    )

    tipo_mime = db.Column(
        db.String(120),
        nullable=False
    )

    tamano_bytes = db.Column(
        db.BigInteger,
        nullable=False
    )

    hash_archivo = db.Column(
        db.String(64),
        nullable=False
    )

    motivo = db.Column(
        db.String(255),
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

    fecha_subida = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    documento = db.relationship(
        "DocumentoEstudiante",
        back_populates="versiones"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_documento",
            "numero_version",
            name="uq_version_documento_numero"
        ),
    )