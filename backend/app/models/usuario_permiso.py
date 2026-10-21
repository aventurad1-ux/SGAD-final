from datetime import datetime

from app.extensions import db


class UsuarioPermiso(db.Model):
    __tablename__ = "usuario_permisos"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    id_permiso = db.Column(
        db.Integer,
        db.ForeignKey(
            "permisos.id_permiso",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    permitido = db.Column(
        db.Boolean,
        nullable=False
    )

    fecha_asignacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="permisos_individuales"
    )

    permiso = db.relationship(
        "Permiso"
    )

    def __repr__(self):
        return (
            f"<UsuarioPermiso "
            f"usuario={self.id_usuario} "
            f"permiso={self.id_permiso}>"
        )