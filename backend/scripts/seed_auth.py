from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.usuario import Usuario
from app.models.permiso import Permiso
from app.services.password_service import hash_password


app = create_app()


with app.app_context():

    # =====================================================
    # ROLES
    # =====================================================

    rol_directora = Role.query.filter_by(
        nombre="Directora"
    ).first()

    if not rol_directora:
        rol_directora = Role(
            nombre="Directora",
            descripcion=(
                "Administración general del SGAD."
            ),
            activo=True,
        )

        db.session.add(rol_directora)
        db.session.flush()

        print("Rol Directora creado.")

    rol_docente = Role.query.filter_by(
        nombre="Docente"
    ).first()

    if not rol_docente:
        rol_docente = Role(
            nombre="Docente",
            descripcion=(
                "Docente del establecimiento."
            ),
            activo=True,
        )

        db.session.add(rol_docente)
        db.session.flush()

        print("Rol Docente creado.")

    # =====================================================
    # PERMISOS DEL SISTEMA
    # =====================================================

    permisos_base = [
        # -------------------------------------------------
        # USUARIOS
        # -------------------------------------------------
        {
            "codigo": "usuarios.ver",
            "nombre": "Ver usuarios",
            "descripcion": (
                "Permite consultar usuarios y sus asignaciones."
            ),
            "modulo": "usuarios",
        },
        {
            "codigo": "usuarios.crear",
            "nombre": "Crear usuarios",
            "descripcion": (
                "Permite crear nuevas cuentas de usuario."
            ),
            "modulo": "usuarios",
        },
        {
            "codigo": "usuarios.editar",
            "nombre": "Editar usuarios",
            "descripcion": (
                "Permite modificar datos, roles y permisos."
            ),
            "modulo": "usuarios",
        },
        {
            "codigo": "usuarios.eliminar",
            "nombre": "Activar o desactivar usuarios",
            "descripcion": (
                "Permite cambiar el estado de una cuenta."
            ),
            "modulo": "usuarios",
        },

        # -------------------------------------------------
        # ESTUDIANTES
        # -------------------------------------------------
        {
            "codigo": "estudiantes.ver",
            "nombre": "Ver estudiantes",
            "descripcion": (
                "Permite consultar estudiantes y matrículas."
            ),
            "modulo": "estudiantes",
        },

        # -------------------------------------------------
        # EXPEDIENTES / DOCUMENTOS
        # -------------------------------------------------
        {
            "codigo": "documentos.ver",
            "nombre": "Ver expedientes",
            "descripcion": (
                "Permite consultar documentos y expedientes."
            ),
            "modulo": "expedientes",
        },
        {
            "codigo": "documentos.subir",
            "nombre": "Subir documentos",
            "descripcion": (
                "Permite agregar documentos a expedientes."
            ),
            "modulo": "expedientes",
        },
        {
            "codigo": "documentos.actualizar",
            "nombre": "Actualizar documentos",
            "descripcion": (
                "Permite agregar nuevas versiones de documentos."
            ),
            "modulo": "expedientes",
        },
        {
            "codigo": "documentos.descargar",
            "nombre": "Descargar documentos",
            "descripcion": (
                "Permite descargar documentos autorizados."
            ),
            "modulo": "expedientes",
        },

        # -------------------------------------------------
        # SOLICITUDES
        # -------------------------------------------------
        {
            "codigo": "solicitudes.ver",
            "nombre": "Ver solicitudes",
            "descripcion": (
                "Permite consultar solicitudes de entrega."
            ),
            "modulo": "solicitudes",
        },
        {
            "codigo": "solicitudes.entregar",
            "nombre": "Realizar entregas",
            "descripcion": (
                "Permite entregar documentos solicitados."
            ),
            "modulo": "solicitudes",
        },
        {
            "codigo": "solicitudes.comprobantes",
            "nombre": "Consultar comprobantes",
            "descripcion": (
                "Permite consultar comprobantes de entrega."
            ),
            "modulo": "solicitudes",
        },

        # -------------------------------------------------
        # REPORTES
        # -------------------------------------------------
        {
            "codigo": "reportes.ver",
            "nombre": "Ver reportes",
            "descripcion": (
                "Permite consultar y generar reportes."
            ),
            "modulo": "reportes",
        },

        # -------------------------------------------------
        # AUDITORÍA
        # -------------------------------------------------
        {
            "codigo": "auditoria.ver",
            "nombre": "Ver auditoría",
            "descripcion": (
                "Permite consultar la bitácora del sistema."
            ),
            "modulo": "auditoria",
        },
    ]

    permisos = {}

    for permiso_data in permisos_base:
        permiso = Permiso.query.filter_by(
            codigo=permiso_data["codigo"]
        ).first()

        if not permiso:
            permiso = Permiso(
                codigo=permiso_data["codigo"],
                nombre=permiso_data["nombre"],
                descripcion=permiso_data["descripcion"],
                modulo=permiso_data["modulo"],
                activo=True,
            )

            db.session.add(permiso)
            db.session.flush()

        else:
            permiso.nombre = (
                permiso_data["nombre"]
            )

            permiso.descripcion = (
                permiso_data["descripcion"]
            )

            permiso.modulo = (
                permiso_data["modulo"]
            )

            permiso.activo = True

        permisos[
            permiso_data["codigo"]
        ] = permiso

    # =====================================================
    # PERMISOS DEL ROL DIRECTORA
    # =====================================================

    permisos_directora = set(
        permisos.keys()
    )

    for codigo in permisos_directora:
        permiso = permisos[codigo]

        if permiso not in rol_directora.permisos:
            rol_directora.permisos.append(
                permiso
            )

    # =====================================================
    # PERMISOS BASE DEL ROL DOCENTE
    # =====================================================

    permisos_docente = {
        "estudiantes.ver",
        "documentos.ver",
        "documentos.subir",
        "documentos.actualizar",
        "documentos.descargar",
        "solicitudes.ver",
        "solicitudes.entregar",
        "solicitudes.comprobantes",
    }

    for codigo in permisos_docente:
        permiso = permisos[codigo]

        if permiso not in rol_docente.permisos:
            rol_docente.permisos.append(
                permiso
            )

    # =====================================================
    # USUARIO DIRECTORA DEMO
    # =====================================================

    usuario_directora = Usuario.query.filter_by(
        correo="directora@sgad.demo"
    ).first()

    if not usuario_directora:
        usuario_directora = Usuario(
            id_rol=rol_directora.id_rol,
            nombres="Directora",
            apellidos="SGAD",
            correo="directora@sgad.demo",
            contrasena_hash=hash_password(
                "Directora2026"
            ),
            activo=True,
        )

        db.session.add(
            usuario_directora
        )

        print(
            "Usuario directora creado."
        )

    else:
        usuario_directora.id_rol = (
            rol_directora.id_rol
        )

        print(
            "El usuario directora ya existe."
        )

    # =====================================================
    # ACTUALIZAR DOCENTE DEMO SI YA EXISTE
    # =====================================================

    usuario_docente = Usuario.query.filter_by(
        correo="docente@sgad.demo"
    ).first()

    if usuario_docente:
        usuario_docente.id_rol = (
            rol_docente.id_rol
        )

        usuario_docente.activo = True

        print(
            "Usuario docente demo actualizado."
        )

    # =====================================================
    # GUARDAR
    # =====================================================

    db.session.commit()

    print(
        "Roles y permisos actualizados correctamente."
    )