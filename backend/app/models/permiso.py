from app.extensions import db


class Permiso(db.Model):
    __tablename__ = "permisos"

    id_permiso = db.Column(
        db.Integer,
        db.Identity(always=True),
        primary_key=True
    )

    codigo = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    descripcion = db.Column(db.Text)

    modulo = db.Column(
        db.String(50),
        nullable=False
    )

    activo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    roles = db.relationship(
        "Role",
        secondary="rol_permisos",
        back_populates="permisos"
    )

    def __repr__(self):
        return f"<Permiso {self.codigo}>"