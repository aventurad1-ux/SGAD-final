from app.extensions import db


class RevisionEntrega(db.Model):
    __tablename__ = "revisiones_entrega"

    id_revision = db.Column(
        db.Integer,
        primary_key=True
    )

    id_version_entrega = db.Column(
        db.Integer,
        db.ForeignKey(
            "versiones_entrega.id_version_entrega",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    id_usuario_revisor = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    resultado = db.Column(
        db.String(25),
        nullable=False
    )

    observaciones = db.Column(
        db.Text,
        nullable=True
    )

    fecha_revision = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    version_entrega = db.relationship(
        "VersionEntrega",
        back_populates="revisiones"
    )

    revisor = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario_revisor]
    )

    __table_args__ = (
        db.CheckConstraint(
            """
            resultado IN (
                'aprobado',
                'correccion_solicitada',
                'rechazado'
            )
            """,
            name="chk_revisiones_resultado"
        ),
        db.CheckConstraint(
            """
            resultado = 'aprobado'
            OR (
                observaciones IS NOT NULL
                AND LENGTH(TRIM(observaciones)) > 0
            )
            """,
            name="chk_revisiones_observaciones"
        ),
    )