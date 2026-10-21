from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import (
    Entrega,
    VersionEntrega,
    RevisionEntrega,
)
from app.utils.permissions import permission_required


review_inbox_bp = Blueprint(
    "review_inbox",
    __name__,
    url_prefix="/api/directora/revision"
)


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
            "id_entrega": entrega.id_entrega,
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
                entrega.fecha_primera_entrega.strftime("%d/%m/%Y")
                if entrega.fecha_primera_entrega
                else None
            ),
            "estado": entrega.estado,
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


@review_inbox_bp.post("/<int:id_entrega>/aprobar")
@permission_required("documentos.ver")
def aprobar_entrega(id_entrega):
    entrega = db.session.get(
        Entrega,
        id_entrega
    )

    if not entrega:
        return jsonify({
            "mensaje": "Entrega no encontrada."
        }), 404

    ultima_version = (
        VersionEntrega.query
        .filter_by(id_entrega=id_entrega)
        .order_by(
            VersionEntrega.numero_version.desc()
        )
        .first()
    )

    if not ultima_version:
        return jsonify({
            "mensaje": "La entrega no tiene una versión para revisar."
        }), 400

    id_usuario = int(get_jwt_identity())

    revision = RevisionEntrega(
        id_version_entrega=
            ultima_version.id_version_entrega,
        id_usuario_revisor=id_usuario,
        resultado="aprobado",
        observaciones=None,
        fecha_revision=datetime.now(
            timezone.utc
        )
    )

    entrega.estado = "aprobado"
    entrega.fecha_actualizacion = datetime.now(
        timezone.utc
    )

    db.session.add(revision)
    db.session.commit()

    return jsonify({
        "mensaje": "Entrega aprobada correctamente.",
        "estado": entrega.estado
    }), 200


@review_inbox_bp.post(
    "/<int:id_entrega>/correccion"
)
@permission_required("documentos.ver")
def solicitar_correccion(id_entrega):
    entrega = db.session.get(
        Entrega,
        id_entrega
    )

    if not entrega:
        return jsonify({
            "mensaje": "Entrega no encontrada."
        }), 404

    data = request.get_json() or {}

    observaciones = (
        data.get("observaciones", "")
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
        .filter_by(id_entrega=id_entrega)
        .order_by(
            VersionEntrega.numero_version.desc()
        )
        .first()
    )

    if not ultima_version:
        return jsonify({
            "mensaje": "La entrega no tiene una versión para revisar."
        }), 400

    id_usuario = int(get_jwt_identity())

    revision = RevisionEntrega(
        id_version_entrega=
            ultima_version.id_version_entrega,
        id_usuario_revisor=id_usuario,
        resultado="correccion_solicitada",
        observaciones=observaciones,
        fecha_revision=datetime.now(
            timezone.utc
        )
    )

    entrega.estado = "correccion_solicitada"
    entrega.fecha_actualizacion = datetime.now(
        timezone.utc
    )

    db.session.add(revision)
    db.session.commit()

    return jsonify({
        "mensaje": "Corrección solicitada correctamente.",
        "estado": entrega.estado
    }), 200