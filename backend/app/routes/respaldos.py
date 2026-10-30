from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    send_file,
)
from flask_jwt_extended import (
    get_jwt_identity,
)

from app.extensions import db
from app.models.respaldo import (
    Respaldo,
)
from app.services.bitacora_service import (
    registrar_actividad,
)
from app.services.respaldo_service import (
    generar_respaldo,
)
from app.services.spaces_service import (
    descargar_respaldo_spaces,
    subir_respaldo_spaces,
)
from app.utils.permissions import (
    permission_required,
)


respaldos_bp = Blueprint(
    "respaldos",
    __name__,
    url_prefix="/api/directora/respaldos"
)


CARPETA_RESPALDOS = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "backups"
).resolve()


# ==========================================
# GENERAR RESPALDO
# ==========================================

@respaldos_bp.post("")
@permission_required(
    "respaldos.generar"
)
def crear_respaldo():

    usuario_id = int(
        get_jwt_identity()
    )

    respaldo = Respaldo(
        id_usuario=usuario_id,
        tipo="Completo",
        estado="En proceso"
    )

    try:
        db.session.add(
            respaldo
        )

        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "mensaje":
                "No fue posible registrar "
                "el respaldo."
        }), 500

    try:
        # ----------------------------------
        # GENERAR ZIP LOCAL
        # ----------------------------------

        resultado = (
            generar_respaldo()
        )

        nombre_archivo = (
            resultado["nombre"]
        )

        ruta_local = (
            CARPETA_RESPALDOS
            / nombre_archivo
        ).resolve()

        if (
            ruta_local.parent
            != CARPETA_RESPALDOS
        ):
            raise RuntimeError(
                "La ruta del respaldo "
                "generado no es válida."
            )

        if not ruta_local.is_file():
            raise FileNotFoundError(
                "El ZIP del respaldo "
                "no fue encontrado."
            )

        # ----------------------------------
        # SUBIR A DIGITALOCEAN SPACES
        # ----------------------------------

        resultado_spaces = (
            subir_respaldo_spaces(
                ruta_local
            )
        )

        # ----------------------------------
        # ACTUALIZAR HISTORIAL
        # ----------------------------------

        respaldo.nombre_archivo = (
            nombre_archivo
        )

        respaldo.tamano = (
            resultado["tamano"]
        )

        respaldo.estado = (
            "Completado"
        )

        respaldo.mensaje_error = None

        # ----------------------------------
        # BITÁCORA
        # ----------------------------------

        registrar_actividad(
            id_usuario=usuario_id,
            accion="CREAR_RESPALDO",
            modulo=(
                "Copias de seguridad"
            ),
            registro=(
                respaldo.nombre_archivo
            ),
            descripcion=(
                "Se generó una copia "
                "de seguridad completa "
                "del sistema y se "
                "almacenó en "
                "DigitalOcean Spaces."
            )
        )

        db.session.commit()

        return jsonify({
            "mensaje": (
                "Respaldo generado y "
                "almacenado en la nube "
                "correctamente."
            ),

            "respaldo": {
                "id_respaldo":
                    respaldo.id_respaldo,

                "nombre":
                    respaldo.nombre_archivo,

                "fecha":
                    respaldo
                    .fecha_creacion
                    .isoformat(),

                "tamano":
                    respaldo.tamano,

                "tipo":
                    respaldo.tipo,

                "estado":
                    respaldo.estado,

                "almacenamiento":
                    "DigitalOcean Spaces",

                "objeto_spaces":
                    resultado_spaces[
                        "clave"
                    ],
            }
        }), 201

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CREAR RESPALDO:",
            repr(error)
        )

        try:
            respaldo = (
                db.session.get(
                    Respaldo,
                    respaldo.id_respaldo
                )
            )

            if respaldo:
                respaldo.estado = (
                    "Fallido"
                )

                respaldo.mensaje_error = (
                    "No fue posible "
                    "generar o almacenar "
                    "el respaldo en "
                    "DigitalOcean Spaces."
                )

                db.session.commit()

        except Exception:
            db.session.rollback()

        return jsonify({
            "mensaje": (
                "No fue posible generar "
                "y almacenar el respaldo."
            )
        }), 500


# ==========================================
# HISTORIAL DE RESPALDOS
# ==========================================

@respaldos_bp.get("")
@permission_required(
    "respaldos.ver"
)
def listar_respaldos():

    registros = (
        Respaldo.query
        .order_by(
            Respaldo
            .fecha_creacion
            .desc()
        )
        .all()
    )

    respaldos = []

    for respaldo in registros:

        responsable = (
            "Usuario no disponible"
        )

        if respaldo.usuario:
            responsable = (
                f"{respaldo.usuario.nombres} "
                f"{respaldo.usuario.apellidos}"
            )

        respaldos.append({
            "id_respaldo":
                respaldo.id_respaldo,

            "nombre":
                respaldo.nombre_archivo,

            "fecha":
                respaldo
                .fecha_creacion
                .isoformat(),

            "tamano":
                respaldo.tamano,

            "tipo":
                respaldo.tipo,

            "estado":
                respaldo.estado,

            "responsable":
                responsable,

            "mensaje_error":
                respaldo.mensaje_error
        })

    return jsonify({
        "respaldos": respaldos
    }), 200


# ==========================================
# DESCARGAR RESPALDO
# ==========================================

@respaldos_bp.get(
    "/<nombre>/descargar"
)
@permission_required(
    "respaldos.descargar"
)
def descargar_respaldo(
    nombre
):

    usuario_id = int(
        get_jwt_identity()
    )

    # --------------------------------------
    # VALIDAR NOMBRE
    # --------------------------------------

    if (
        nombre != Path(nombre).name
        or not nombre.startswith(
            "respaldo_sgad_"
        )
        or not nombre.endswith(
            ".zip"
        )
    ):
        return jsonify({
            "mensaje":
                "Nombre de respaldo "
                "no válido."
        }), 400

    # --------------------------------------
    # COMPROBAR REGISTRO
    # --------------------------------------

    respaldo = (
        Respaldo.query.filter_by(
            nombre_archivo=nombre,
            estado="Completado"
        )
        .first()
    )

    if not respaldo:
        return jsonify({
            "mensaje":
                "El respaldo no está "
                "disponible."
        }), 404

    archivo = (
        CARPETA_RESPALDOS
        / nombre
    ).resolve()

    if (
        archivo.parent
        != CARPETA_RESPALDOS
    ):
        return jsonify({
            "mensaje":
                "Ruta de respaldo "
                "no válida."
        }), 400

    # --------------------------------------
    # SI NO EXISTE LOCALMENTE,
    # RECUPERAR DESDE SPACES
    # --------------------------------------

    if not archivo.is_file():

        try:
            descargar_respaldo_spaces(
                nombre,
                archivo
            )

        except FileNotFoundError:
            return jsonify({
                "mensaje": (
                    "El respaldo no existe "
                    "localmente ni en "
                    "DigitalOcean Spaces."
                )
            }), 404

        except Exception as error:
            print(
                "ERROR RECUPERAR "
                "RESPALDO DE SPACES:",
                repr(error)
            )

            return jsonify({
                "mensaje": (
                    "No fue posible "
                    "recuperar el respaldo "
                    "desde la nube."
                )
            }), 500

    # --------------------------------------
    # BITÁCORA
    # --------------------------------------

    try:
        registrar_actividad(
            id_usuario=usuario_id,
            accion=(
                "DESCARGAR_RESPALDO"
            ),
            modulo=(
                "Copias de seguridad"
            ),
            registro=nombre,
            descripcion=(
                "Se descargó una copia "
                "de seguridad del sistema."
            )
        )

        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "mensaje": (
                "No fue posible registrar "
                "la descarga del respaldo."
            )
        }), 500

    # --------------------------------------
    # ENVIAR ZIP
    # --------------------------------------

    return send_file(
        archivo,
        as_attachment=True,
        download_name=archivo.name
    )