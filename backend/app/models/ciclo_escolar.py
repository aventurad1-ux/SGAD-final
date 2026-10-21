from app.extensions import db


class CicloEscolar(db.Model):
    __tablename__ = "ciclos_escolares"

    id_ciclo = db.Column(
        db.Integer,
        primary_key=True
    )

    anio = db.Column(
        db.Integer,
        nullable=False,
        unique=True
    )

    fecha_inicio = db.Column(
        db.Date,
        nullable=False
    )

    fecha_fin = db.Column(
        db.Date,
        nullable=False
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="activo",
        server_default="activo"
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    solicitudes = db.relationship(
        "Solicitud",
        back_populates="ciclo",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "anio BETWEEN 2000 AND 2100",
            name="chk_ciclos_anio"
        ),
        db.CheckConstraint(
            "fecha_fin >= fecha_inicio",
            name="chk_ciclos_fechas"
        ),
        db.CheckConstraint(
            "estado IN ('activo', 'cerrado')",
            name="chk_ciclos_estado"
        ),
    )