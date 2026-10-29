from app import create_app
from app.extensions import db
from app.models.permiso import Permiso
from app.models.role import Role


app = create_app()

with app.app_context():

    # Buscar el rol de directora
    directora = Role.query.filter_by(
        nombre="Directora"
    ).first()

    if directora is None:
        print("No se encontró el rol Directora.")

    elif not directora.activo:
        print("El rol Directora está inactivo.")

    else:

        # Permisos necesarios para nuestro módulo
        permisos_respaldos = [
            {
                "codigo": "respaldos.ver",
                "nombre": "Ver respaldos",
                "descripcion": "Permite consultar los respaldos.",
                "modulo": "respaldos"
            },
            {
                "codigo": "respaldos.generar",
                "nombre": "Generar respaldos",
                "descripcion": "Permite crear copias de seguridad.",
                "modulo": "respaldos"
            },
            {
                "codigo": "respaldos.descargar",
                "nombre": "Descargar respaldos",
                "descripcion": "Permite descargar copias de seguridad.",
                "modulo": "respaldos"
            }
        ]

        try:
            for datos in permisos_respaldos:

                # Revisar si el permiso ya existe
                permiso = Permiso.query.filter_by(
                    codigo=datos["codigo"]
                ).first()

                if permiso is None:
                    permiso = Permiso(**datos)
                    db.session.add(permiso)

                # Activar el permiso
                permiso.activo = True

                # Asignarlo a la directora si aún no lo tiene
                if permiso not in directora.permisos:
                    directora.permisos.append(permiso)

            db.session.commit()

            print("Permisos de respaldos configurados correctamente.")

        except Exception as error:
            db.session.rollback()
            print("Error al configurar los permisos:", error)