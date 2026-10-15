from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.usuario import Usuario
from app.models.permiso import Permiso
from app.services.password_service import hash_password


app = create_app()


with app.app_context():

    rol_directora = Role.query.filter_by(
        nombre="Directora"
    ).first()

    if not rol_directora:
        rol_directora = Role(
            nombre="Directora",
            descripcion="Rol con acceso administrativo al SGAD",
            activo=True
        )

        db.session.add(rol_directora)
        db.session.commit()

        print("Rol Directora creado.")

    permisos_base = [
        {
            "codigo": "usuarios.ver",
            "nombre": "Ver usuarios",
            "modulo": "usuarios"
        },
        {
            "codigo": "usuarios.crear",
            "nombre": "Crear usuarios",
            "modulo": "usuarios"
        },
        {
            "codigo": "usuarios.editar",
            "nombre": "Editar usuarios",
            "modulo": "usuarios"
        },
        {
            "codigo": "usuarios.eliminar",
            "nombre": "Eliminar usuarios",
            "modulo": "usuarios"
        },
        {
            "codigo": "estudiantes.ver",
            "nombre": "Ver estudiantes",
            "modulo": "estudiantes"
        },
        {
            "codigo": "documentos.ver",
            "nombre": "Ver documentos",
            "modulo": "documentos"
        },
        {
            "codigo": "reportes.ver",
            "nombre": "Ver reportes",
            "modulo": "reportes"
        },
        {
            "codigo": "auditoria.ver",
            "nombre": "Ver auditoría",
            "modulo": "auditoria"
        }
    ]

    for permiso_data in permisos_base:

        permiso = Permiso.query.filter_by(
            codigo=permiso_data["codigo"]
        ).first()

        if not permiso:
            permiso = Permiso(
                codigo=permiso_data["codigo"],
                nombre=permiso_data["nombre"],
                modulo=permiso_data["modulo"],
                activo=True
            )

            db.session.add(permiso)
            db.session.flush()

        if permiso not in rol_directora.permisos:
            rol_directora.permisos.append(permiso)

    usuario_directora = Usuario.query.filter_by(
        correo="directora@sgad.demo"
    ).first()

    if not usuario_directora:
        usuario_directora = Usuario(
            id_rol=rol_directora.id_rol,
            nombres="Directora",
            apellidos="SGAD",
            correo="directora@sgad.demo",
            contrasena_hash=hash_password("Directora2026"),
            activo=True
        )

        db.session.add(usuario_directora)

        print("Usuario directora creado.")

    else:
        print("El usuario directora ya existe.")

    db.session.commit()

    print("Permisos base creados y asignados a Directora.")