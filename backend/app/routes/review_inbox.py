from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_file,
)
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import (
    Entrega,
    VersionEntrega,
    RevisionEntrega,
)
from app.services.bitacora_service import registrar_actividad
from app.utils.permissions import permission_required


review_inbox_bp = Blueprint(
    "review_inbox",
    __name__,
    url_prefix="/api/directora/revision"
)


# =========================================================
# UTILIDADES
# =========================================================

def backend_root():
    """
    current_app.root_path apunta a backend/app.
    Subimos un nivel para llegar a backend.
    """
    return Path(
        current_app.root_path
    ).parent


def obtener_ruta_version(version):
    if not version or not version.ruta_archivo:
        return None

    ruta = Path(
        version.ruta_archivo
    )

    if ruta.is_absolute():
        return ruta

    return (
        backend_root()
        / ruta
    )


# =========================================================
# LISTAR ENTREGAS PARA REVISIÓN
# =========================================================

@review_inbox_bp.get("")
@permission_required("documentos.ver")
def listar_entregas_revision():
    entregas = (
        db.session.query(Entrega)
        .order_by(Entrega.id_entrega.desc())
        .all()
    )

    resultado = []

    for entrega in entregas:
        destinatario = entrega.destinatario
        requisito = entrega.requisito

        solicitud = (
            destinatario.solicitud
            if destinatario
            else None
        )

        docente = (
            destinatario.docente
            if destinatario
            else None
        )

        ultima_version = (
            VersionEntrega.query
            .filter_by(
                id_entrega=entrega.id_entrega
            )
            .order_by(
                VersionEntrega.numero_version.desc()
            )
            .first()
        )

        resultado.append({
            "id_entrega":
                entrega.id_entrega,

            "solicitud": (
                solicitud.titulo
                if solicitud
                else ""
            ),

            "codigo": (
                f"SOL-{solicitud.id_solicitud:04d}"
                if solicitud
                else ""
            ),

            "docente": (
                f"{docente.nombres} {docente.apellidos}".strip()
                if docente
                else ""
            ),

            "fecha": (
                entrega.fecha_primera_entrega.strftime(
                    "%d/%m/%Y"
                )
                if entrega.fecha_primera_entrega
                else None
            ),

            "estado":
                entrega.estado,

            "archivo": (
                ultima_version.nombre_archivo
                if ultima_version
                else None
            ),

            "version": (
                ultima_version.numero_version
                if ultima_version
                else None
            ),

            "id_version_entrega": (
                ultima_version.id_version_entrega
                if ultima_version
                else None
            ),
        })

    return jsonify({
        "entregas": resultado
    }), 200


# =========================================================
# VER ARCHIVO DE UNA ENTREGA
# =========================================================

@review_inbox_bp.get(
    "/versiones/<int:id_version>/ver"
)
@permission_required("documentos.ver")
def ver_archivo_revision(
    id_version
):
    version = db.session.get(
        VersionEntrega,
        id_version
    )

    if not version:
        return jsonify({
            "mensaje":
                "La versión del archivo no existe."
        }), 404

    entrega = version.entrega

    if not entrega:
        return jsonify({
            "mensaje":
                "La entrega asociada no existe."
        }), 404

    ruta = obtener_ruta_version(
        version
    )

    if (
        not ruta
        or not ruta.exists()
        or not ruta.is_file()
    ):
        return jsonify({
            "mensaje":
                "El archivo físico no fue encontrado."
        }), 404

    return send_file(
        ruta,
        mimetype=(
            version.tipo_mime
            or "application/octet-stream"
        ),
        as_attachment=False,
        download_name=(
            version.nombre_archivo
        )
    )


# =========================================================
# DESCARGAR ARCHIVO DE UNA ENTREGA
# =========================================================

@review_inbox_bp.get(
    "/versiones/<int:id_version>/descargar"
)
@permission_required("documentos.ver")
def descargar_archivo_revision(
    id_version
):
    version = db.session.get(
        VersionEntrega,
        id_version
    )

    if not version:
        return jsonify({
            "mensaje":
                "La versión del archivo no existe."
        }), 404

    entrega = version.entrega

    if not entrega:
        return jsonify({
            "mensaje":
                "La entrega asociada no existe."
        }), 404

    ruta = obtener_ruta_version(
        version
    )

    if (
        not ruta
        or not ruta.exists()
        or not ruta.is_file()
    ):
        return jsonify({
            "mensaje":
                "El archivo físico no fue encontrado."
        }), 404

    return send_file(
        ruta,
        mimetype=(
            version.tipo_mime
            or "application/octet-stream"
        ),
        as_attachment=True,
        download_name=(
            version.nombre_archivo
        )
    )


# =========================================================
# APROBAR ENTREGA
# =========================================================

@review_inbox_bp.post(
    "/<int:id_entrega>/aprobar"
)
@permission_required("documentos.ver")
def aprobar_entrega(
    id_entrega
):
    entrega = db.session.get(
        Entrega,
        id_entrega
    )

    if not entrega:
        return jsonify({
            "mensaje":
                "Entrega no encontrada."
        }), 404

    ultima_version = (
        VersionEntrega.query
        .filter_by(
            id_entrega=id_entrega
        )
        .order_by(
            VersionEntrega.numero_version.desc()
        )
        .first()
    )

    if not ultima_version:
        return jsonify({
            "mensaje":
                "La entrega no tiene una versión para revisar."
        }), 400

    id_usuario = int(
        get_jwt_identity()
    )

    destinatario = (
        entrega.destinatario
    )

    solicitud = (
        destinatario.solicitud
        if destinatario
        else None
    )

    codigo_solicitud = (
        f"SOL-{solicitud.id_solicitud:04d}"
        if solicitud
        else f"ENT-{entrega.id_entrega:04d}"
    )

    revision = RevisionEntrega(
        id_version_entrega=(
            ultima_version.id_version_entrega
        ),
        id_usuario_revisor=(
            id_usuario
        ),
        resultado=(
            "aprobado"
        ),
        observaciones=(
            None
        ),
        fecha_revision=(
            datetime.now(
                timezone.utc
            )
        )
    )

    entrega.estado = (
        "aprobado"
    )

    entrega.fecha_actualizacion = (
        datetime.now(
            timezone.utc
        )
    )

    try:
        db.session.add(
            revision
        )

        registrar_actividad(
            id_usuario=id_usuario,
            accion="APROBAR_ENTREGA",
            modulo="Solicitudes y entregas",
            registro=codigo_solicitud,
            descripcion=(
                f"Se aprobó la entrega "
                f"#{entrega.id_entrega}, "
                f"versión "
                f"{ultima_version.numero_version}."
            )
        )

        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR APROBAR ENTREGA:",
            repr(error)
        )

        return jsonify({
            "mensaje":
                "No fue posible aprobar la entrega."
        }), 500

    return jsonify({
        "mensaje":
            "Entrega aprobada correctamente.",

        "estado":
            entrega.estado
    }), 200


# =========================================================
# SOLICITAR CORRECCIÓN
# =========================================================

@review_inbox_bp.post(
    "/<int:id_entrega>/correccion"
)
@permission_required("documentos.ver")
def solicitar_correccion(
    id_entrega
):
    entrega = db.session.get(
        Entrega,
        id_entrega
    )

    if not entrega:
        return jsonify({
            "mensaje":
                "Entrega no encontrada."
        }), 404

    data = (
        request.get_json()
        or {}
    )

    observaciones = (
        data.get(
            "observaciones",
            ""
        )
        .strip()
    )

    if len(observaciones) < 8:
        return jsonify({
            "mensaje": (
                "Las observaciones deben tener "
                "al menos 8 caracteres."
            )
        }), 400

    ultima_version = (
        VersionEntrega.query
        .filter_by(
            id_entrega=id_entrega
        )
        .order_by(
            VersionEntrega.numero_version.desc()
        )
        .first()
    )

    if not ultima_version:
        return jsonify({
            "mensaje":
                "La entrega no tiene una versión para revisar."
        }), 400

    id_usuario = int(
        get_jwt_identity()
    )

    destinatario = (
        entrega.destinatario
    )

    solicitud = (
        destinatario.solicitud
        if destinatario
        else None
    )

    codigo_solicitud = (
        f"SOL-{solicitud.id_solicitud:04d}"
        if solicitud
        else f"ENT-{entrega.id_entrega:04d}"
    )

    revision = RevisionEntrega(
        id_version_entrega=(
            ultima_version.id_version_entrega
        ),
        id_usuario_revisor=(
            id_usuario
        ),
        resultado=(
            "correccion_solicitada"
        ),
        observaciones=(
            observaciones
        ),
        fecha_revision=(
            datetime.now(
                timezone.utc
            )
        )
    )

    entrega.estado = (
        "correccion_solicitada"
    )

    entrega.fecha_actualizacion = (
        datetime.now(
            timezone.utc
        )
    )

    try:
        db.session.add(
            revision
        )

        registrar_actividad(
            id_usuario=id_usuario,
            accion="SOLICITAR_CORRECCION",
            modulo="Solicitudes y entregas",
            registro=codigo_solicitud,
            descripcion=(
                f"Se solicitó corrección "
                f"para la entrega "
                f"#{entrega.id_entrega}, "
                f"versión "
                f"{ultima_version.numero_version}."
            )
        )

        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR SOLICITAR CORRECCIÓN:",
            repr(error)
        )

        return jsonify({
            "mensaje":
                "No fue posible solicitar la corrección."
        }), 500

    return jsonify({
        "mensaje":
            "Corrección solicitada correctamente.",

        "estado":
            entrega.estado
    }), 200