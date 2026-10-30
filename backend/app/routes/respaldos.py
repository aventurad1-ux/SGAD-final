from pathlib import Path

from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.respaldo import Respaldo
from app.services.respaldo_service import generar_respaldo
from app.services.bitacora_service import registrar_actividad
from app.utils.permissions import permission_required


# Crear el módulo de respaldos
respaldos_bp = Blueprint(
    "respaldos",
    __name__,
    url_prefix="/api/directora/respaldos"
)


# Carpeta donde se guardan los archivos ZIP
CARPETA_RESPALDOS = (
    Path(__file__).resolve().parents[2] / "backups"
).resolve()


# ==========================================
# GENERAR RESPALDO
# ==========================================

@respaldos_bp.post("")
@permission_required("respaldos.generar")
def crear_respaldo():

    # Obtener el usuario que inició sesión
    usuario_id = int(get_jwt_identity())

    # Registrar el intento antes de generar el ZIP
    respaldo = Respaldo(
        id_usuario=usuario_id,
        tipo="Completo",
        estado="En proceso"
    )

    try:
        db.session.add(respaldo)
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "mensaje": "No fue posible registrar el respaldo."
        }), 500

    # Generar el respaldo
    try:
        resultado = generar_respaldo()

        # Actualizar el historial
        respaldo.nombre_archivo = resultado["nombre"]
        respaldo.tamano = resultado["tamano"]
        respaldo.estado = "Completado"

        # Registrar la acción en bitácora
        registrar_actividad(
            id_usuario=usuario_id,
            accion="CREAR_RESPALDO",
            modulo="Copias de seguridad",
            registro=respaldo.nombre_archivo,
            descripcion=(
                "Se generó una copia de seguridad "
                "completa del sistema."
            )
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Respaldo generado correctamente.",
            "respaldo": {
                "id_respaldo": respaldo.id_respaldo,
                "nombre": respaldo.nombre_archivo,
                "fecha": respaldo.fecha_creacion.isoformat(),
                "tamano": respaldo.tamano,
                "tipo": respaldo.tipo,
                "estado": respaldo.estado
            }
        }), 201

    except Exception:
        db.session.rollback()

        # Registrar que ocurrió un error
        try:
            respaldo = db.session.get(
                Respaldo,
                respaldo.id_respaldo
            )

            if respaldo:
                respaldo.estado = "Fallido"
                respaldo.mensaje_error = (
                    "No fue posible completar el respaldo."
                )

                db.session.commit()

        except Exception:
            db.session.rollback()

        return jsonify({
            "mensaje": "No fue posible generar el respaldo."
        }), 500


# ==========================================
# HISTORIAL DE RESPALDOS
# ==========================================

@respaldos_bp.get("")
@permission_required("respaldos.ver")
def listar_respaldos():

    registros = (
        Respaldo.query
        .order_by(Respaldo.fecha_creacion.desc())
        .all()
    )

    respaldos = []

    for respaldo in registros:

        # Obtener el nombre del usuario responsable
        responsable = "Usuario no disponible"

        if respaldo.usuario:
            responsable = (
                f"{respaldo.usuario.nombres} "
                f"{respaldo.usuario.apellidos}"
            )

        respaldos.append({
            "id_respaldo": respaldo.id_respaldo,
            "nombre": respaldo.nombre_archivo,
            "fecha": respaldo.fecha_creacion.isoformat(),
            "tamano": respaldo.tamano,
            "tipo": respaldo.tipo,
            "estado": respaldo.estado,
            "responsable": responsable,
            "mensaje_error": respaldo.mensaje_error
        })

    return jsonify({
        "respaldos": respaldos
    }), 200


# ==========================================
# DESCARGAR RESPALDO
# ==========================================

@respaldos_bp.get("/<nombre>/descargar")
@permission_required("respaldos.descargar")
def descargar_respaldo(nombre):

    usuario_id = int(get_jwt_identity())

    # Validar el nombre del archivo
    if (
        nombre != Path(nombre).name
        or not nombre.startswith("respaldo_sgad_")
        or not nombre.endswith(".zip")
    ):
        return jsonify({
            "mensaje": "Nombre de respaldo no válido."
        }), 400

    # Comprobar que el respaldo está registrado
    respaldo = Respaldo.query.filter_by(
        nombre_archivo=nombre,
        estado="Completado"
    ).first()

    if not respaldo:
        return jsonify({
            "mensaje": "El respaldo no está disponible."
        }), 404

    archivo = (CARPETA_RESPALDOS / nombre).resolve()

    # Evitar acceder a archivos fuera de backups
    if archivo.parent != CARPETA_RESPALDOS:
        return jsonify({
            "mensaje": "Ruta de respaldo no válida."
        }), 400

    if not archivo.is_file():
        return jsonify({
            "mensaje": "El archivo de respaldo no existe."
        }), 404

    # Registrar descarga en bitácora
    try:
        registrar_actividad(
            id_usuario=usuario_id,
            accion="DESCARGAR_RESPALDO",
            modulo="Copias de seguridad",
            registro=nombre,
            descripcion=(
                "Se descargó una copia de seguridad "
                "del sistema."
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

    return send_file(
        archivo,
        as_attachment=True,
        download_name=archivo.name
    )