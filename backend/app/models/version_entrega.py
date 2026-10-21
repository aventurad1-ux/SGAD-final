from app.extensions import db


class VersionEntrega(db.Model):
    __tablename__ = "versiones_entrega"

    id_version_entrega = db.Column(
        db.Integer,
        primary_key=True
    )

    id_entrega = db.Column(
        db.Integer,
        db.ForeignKey(
            "entregas.id_entrega",
            ondelete="RESTRICT"
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
        db.Text,
        nullable=False,
        unique=True
    )

    tipo_mime = db.Column(
        db.String(100),
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

    comentario = db.Column(
        db.Text,
        nullable=True
    )

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    fecha_subida = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    entrega = db.relationship(
        "Entrega",
        back_populates="versiones"
    )

    usuario = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario]
    )

    revisiones = db.relationship(
        "RevisionEntrega",
        back_populates="version_entrega",
        lazy=True
    )

    __table_args__ = (
        db.UniqueConstraint(
            "id_entrega",
            "numero_version",
            name="uq_version_entrega"
        ),
        db.CheckConstraint(
            "numero_version > 0",
            name="chk_version_entrega_numero"
        ),
        db.CheckConstraint(
            "tamano_bytes > 0",
            name="chk_version_entrega_tamano"
        ),
        db.CheckConstraint(
            "hash_archivo ~ '^[0-9a-fA-F]{64}$'",
            name="chk_version_entrega_hash"
        ),
    )