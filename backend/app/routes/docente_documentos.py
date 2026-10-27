from pathlib import Path

from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import get_jwt_identity

from app.models import (
    Entrega,
    SolicitudDestinatario,
    VersionEntrega,
)
from app.utils.permissions import permission_required


docente_documentos_bp = Blueprint(
    "docente_documentos",
    __name__,
    url_prefix="/api/docente/documentos",
)


# =========================================================
# UTILIDADES
# =========================================================

def obtener_id_docente():
    identidad = get_jwt_identity()

    try:
        return int(identidad)
    except (TypeError, ValueError):
        return None


def obtener_ultima_version(entrega):
    return (
        VersionEntrega.query
        .filter_by(
            id_entrega=entrega.id_entrega
        )
        .order_by(
            VersionEntrega.numero_version.desc()
        )
        .first()
    )


def obtener_versiones(entrega):
    return (
        VersionEntrega.query
        .filter_by(
            id_entrega=entrega.id_entrega
        )
        .order_by(
            VersionEntrega.numero_version.desc()
        )
        .all()
    )


def serializar_version(version):
    if not version:
        return None

    return {
        "id_version_entrega":
            version.id_version_entrega,

        "numero_version":
            version.numero_version,

        "nombre_archivo":
            version.nombre_archivo,

        "tipo_mime":
            version.tipo_mime,

        "tamano_bytes":
            version.tamano_bytes,

        "fecha_subida": (
            version.fecha_subida.isoformat()
            if version.fecha_subida
            else None
        ),

        "comentario":
            version.comentario,
    }


def serializar_documento(entrega):
    destinatario = entrega.destinatario

    solicitud = (
        destinatario.solicitud
        if destinatario
        else None
    )

    requisito = entrega.requisito

    ultima_version = obtener_ultima_version(
        entrega
    )

    versiones = obtener_versiones(
        entrega
    )

    formatos = []

    if (
        requisito
        and requisito.formato_permitido
    ):
        formatos = [
            formato.strip()
            for formato
            in requisito.formato_permitido.split(",")
            if formato.strip()
        ]

    return {
        "id_entrega":
            entrega.id_entrega,

        "id_destinatario": (
            destinatario.id_destinatario
            if destinatario
            else None
        ),

        "id_solicitud": (
            solicitud.id_solicitud
            if solicitud
            else None
        ),

        "documento": (
            solicitud.titulo
            if solicitud
            else (
                requisito.nombre_documento
                if requisito
                else "Documento"
            )
        ),

        "codigo": (
            f"ENT-{entrega.id_entrega:04d}"
        ),

        "descripcion": (
            solicitud.descripcion
            if solicitud
            else None
        ),

        "fecha_limite": (
            solicitud.fecha_limite.isoformat()
            if (
                solicitud
                and solicitud.fecha_limite
            )
            else None
        ),

        "prioridad": (
            solicitud.prioridad
            if solicitud
            else None
        ),

        "id_ciclo": (
            solicitud.id_ciclo
            if solicitud
            else None
        ),

        "formatos_permitidos":
            formatos,

        "estado":
            entrega.estado,

        "observaciones":
            entrega.observaciones,

        "fecha_primera_entrega": (
            entrega.fecha_primera_entrega.isoformat()
            if entrega.fecha_primera_entrega
            else None
        ),

        "fecha_actualizacion": (
            entrega.fecha_actualizacion.isoformat()
            if entrega.fecha_actualizacion
            else None
        ),

        "ultima_version":
            serializar_version(
                ultima_version
            ),

        "versiones": [
            serializar_version(version)
            for version in versiones
        ],
    }


def obtener_entrega_docente(
    id_entrega,
    id_docente
):
    return (
        Entrega.query
        .join(
            SolicitudDestinatario,
            Entrega.id_destinatario
            == SolicitudDestinatario.id_destinatario,
        )
        .filter(
            Entrega.id_entrega
            == id_entrega,

            SolicitudDestinatario.id_docente
            == id_docente,
        )
        .first()
    )


def obtener_version_docente(
    id_version,
    id_docente
):
    return (
        VersionEntrega.query
        .join(
            Entrega,
            VersionEntrega.id_entrega
            == Entrega.id_entrega,
        )
        .join(
            SolicitudDestinatario,
            Entrega.id_destinatario
            == SolicitudDestinatario.id_destinatario,
        )
        .filter(
            VersionEntrega.id_version_entrega
            == id_version,

            SolicitudDestinatario.id_docente
            == id_docente,
        )
        .first()
    )


def obtener_ruta_archivo(version):
    if not version:
        return None

    ruta = Path(
        version.ruta_archivo
    )

    if not ruta.is_absolute():
        ruta = (
            Path(__file__)
            .resolve()
            .parents[2]
            / ruta
        )

    return ruta.resolve()


# =========================================================
# LISTAR MIS DOCUMENTOS
# =========================================================

@docente_documentos_bp.get("")
@permission_required("solicitudes.ver")
def listar_documentos():
    id_docente = obtener_id_docente()

    if not id_docente:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 401

    entregas = (
        Entrega.query
        .join(
            SolicitudDestinatario,
            Entrega.id_destinatario
            == SolicitudDestinatario.id_destinatario,
        )
        .filter(
            SolicitudDestinatario.id_docente
            == id_docente,

            Entrega.estado
            != "pendiente",
        )
        .order_by(
            Entrega.fecha_actualizacion.desc(),
            Entrega.fecha_primera_entrega.desc(),
            Entrega.id_entrega.desc(),
        )
        .all()
    )

    documentos = [
        serializar_documento(entrega)
        for entrega in entregas
    ]

    return jsonify({
        "documentos":
            documentos,

        "total":
            len(documentos),
    }), 200


# =========================================================
# VER DETALLE
# =========================================================

@docente_documentos_bp.get(
    "/<int:id_entrega>"
)
@permission_required("solicitudes.ver")
def ver_detalle_documento(
    id_entrega
):
    id_docente = obtener_id_docente()

    if not id_docente:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 401

    entrega = obtener_entrega_docente(
        id_entrega,
        id_docente,
    )

    if not entrega:
        return jsonify({
            "mensaje":
                "El documento no existe o no pertenece al docente."
        }), 404

    return jsonify({
        "documento":
            serializar_documento(
                entrega
            )
    }), 200


# =========================================================
# VER ARCHIVO
# =========================================================

@docente_documentos_bp.get(
    "/versiones/<int:id_version>/ver"
)
@permission_required("solicitudes.ver")
def ver_archivo(
    id_version
):
    id_docente = obtener_id_docente()

    if not id_docente:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 401

    version = obtener_version_docente(
        id_version,
        id_docente,
    )

    if not version:
        return jsonify({
            "mensaje":
                "El archivo no existe o no pertenece al docente."
        }), 404

    ruta = obtener_ruta_archivo(
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
        mimetype=version.tipo_mime,
        as_attachment=False,
        download_name=
            version.nombre_archivo,
    )


# =========================================================
# DESCARGAR ARCHIVO
# =========================================================

@docente_documentos_bp.get(
    "/versiones/<int:id_version>/descargar"
)
@permission_required("solicitudes.ver")
def descargar_archivo(
    id_version
):
    id_docente = obtener_id_docente()

    if not id_docente:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 401

    version = obtener_version_docente(
        id_version,
        id_docente,
    )

    if not version:
        return jsonify({
            "mensaje":
                "El archivo no existe o no pertenece al docente."
        }), 404

    ruta = obtener_ruta_archivo(
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
        mimetype=version.tipo_mime,
        as_attachment=True,
        download_name=
            version.nombre_archivo,
    )