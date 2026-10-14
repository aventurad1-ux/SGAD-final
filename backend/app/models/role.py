from app.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id_rol = db.Column(
        db.Integer,
        db.Identity(always=True),
        primary_key=True
    )

    nombre = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    descripcion = db.Column(db.Text)

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    usuarios = db.relationship(
        "Usuario",
        back_populates="rol"
    )

    permisos = db.relationship(
        "Permiso",
        secondary="rol_permisos",
        back_populates="roles"
    )

    def __repr__(self):
        return f"<Role {self.nombre}>"