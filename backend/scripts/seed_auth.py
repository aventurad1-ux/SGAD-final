from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.usuario import Usuario
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
        db.session.commit()

        print("Usuario directora creado.")

    else:
        print("El usuario directora ya existe.")