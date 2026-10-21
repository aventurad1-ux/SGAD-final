from app.extensions import db


class Solicitud(db.Model):
    __tablename__ = "solicitudes"

    id_solicitud = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=False
    )

    id_usuario_creador = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    id_ciclo = db.Column(
        db.Integer,
        db.ForeignKey(
            "ciclos_escolares.id_ciclo",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    fecha_publicacion = db.Column(
        db.DateTime,
        nullable=True
    )

    fecha_limite = db.Column(
        db.DateTime,
        nullable=False
    )

    prioridad = db.Column(
        db.String(20),
        nullable=False,
        default="normal",
        server_default="normal"
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="borrador",
        server_default="borrador"
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=True
    )

    creador = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario_creador]
    )

    ciclo = db.relationship(
        "CicloEscolar",
        back_populates="solicitudes"
    )

    destinatarios = db.relationship(
        "SolicitudDestinatario",
        back_populates="solicitud",
        lazy=True
    )

    requisitos = db.relationship(
        "SolicitudRequisito",
        back_populates="solicitud",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            """
            prioridad IN (
                'baja',
                'normal',
                'alta',
                'urgente'
            )
            """,
            name="chk_solicitudes_prioridad"
        ),
        db.CheckConstraint(
            """
            estado IN (
                'borrador',
                'publicada',
                'cerrada',
                'cancelada'
            )
            """,
            name="chk_solicitudes_estado"
        ),
        db.CheckConstraint(
            """
            fecha_publicacion IS NULL
            OR fecha_limite > fecha_publicacion
            """,
            name="chk_solicitudes_fechas"
        ),
        db.CheckConstraint(
            """
            estado = 'borrador'
            OR fecha_publicacion IS NOT NULL
            """,
            name="chk_solicitudes_publicacion"
        ),
    )