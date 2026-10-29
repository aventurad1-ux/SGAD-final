from app.extensions import db


class DocumentoInstitucional(db.Model):
    __tablename__ = "documentos_institucionales"

    id_documento = db.Column(
        db.Integer,
        primary_key=True
    )

    codigo = db.Column(
        db.String(30),
        nullable=False,
        unique=True
    )

    id_ciclo = db.Column(
        db.Integer,
        db.ForeignKey(
            "ciclos_escolares.id_ciclo",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    id_categoria = db.Column(
        db.Integer,
        db.ForeignKey(
            "categorias_repositorio.id_categoria",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    descripcion = db.Column(
        db.Text,
        nullable=True
    )

    fecha_documental = db.Column(
        db.Date,
        nullable=False
    )

    nivel_acceso = db.Column(
        db.String(30),
        nullable=False,
        default="direccion",
        server_default="direccion"
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="Vigente",
        server_default="Vigente"
    )

    version_actual = db.Column(
        db.Integer,
        nullable=False,
        default=1,
        server_default="1"
    )

    id_usuario_responsable = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    en_papelera = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    fecha_papelera = db.Column(
        db.DateTime,
        nullable=True
    )

    id_usuario_papelera = db.Column(
        db.Integer,
        db.ForeignKey(
            "usuarios.id_usuario",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    ciclo = db.relationship(
        "CicloEscolar",
        lazy="joined"
    )

    categoria = db.relationship(
        "CategoriaRepositorio",
        back_populates="documentos",
        lazy="joined"
    )

    responsable = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario_responsable],
        lazy="joined"
    )

    usuario_papelera = db.relationship(
        "Usuario",
        foreign_keys=[id_usuario_papelera],
        lazy="joined"
    )

    versiones = db.relationship(
        "VersionDocumentoInstitucional",
        back_populates="documento",
        cascade="all, delete-orphan",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "nivel_acceso IN ('direccion', 'direccion_docentes')",
            name="chk_documentos_institucionales_acceso"
        ),
        db.CheckConstraint(
            "estado IN ('Vigente', 'Archivado')",
            name="chk_documentos_institucionales_estado"
        ),
    )