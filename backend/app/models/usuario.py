from datetime import datetime

from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(
        db.Integer,
        db.Identity(always=True),
        primary_key=True
    )

    id_rol = db.Column(
        db.Integer,
        db.ForeignKey(
            "roles.id_rol",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    nombres = db.Column(
        db.String(100),
        nullable=False
    )

    apellidos = db.Column(
        db.String(100),
        nullable=False
    )

    correo = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    contrasena_hash = db.Column(
        db.Text,
        nullable=False
    )

    telefono = db.Column(
        db.String(20)
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    fecha_actualizacion = db.Column(
        db.DateTime
    )

    rol = db.relationship(
        "Role",
        back_populates="usuarios"
    )

    permisos_individuales = db.relationship(
        "UsuarioPermiso",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    refresh_tokens = db.relationship(
        "RefreshToken",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Usuario {self.correo}>"