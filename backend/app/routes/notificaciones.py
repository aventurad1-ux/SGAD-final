from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import Notificacion
from app.utils.permissions import permission_required


notificaciones_bp = Blueprint(
    "notificaciones",
    __name__,
    url_prefix="/api/notificaciones",
)


def obtener_id_usuario():
    try:
        return int(
            get_jwt_identity()
        )
    except (TypeError, ValueError):
        return None


@notificaciones_bp.get("")
@permission_required("documentos.ver")
def listar_notificaciones():
    id_usuario = obtener_id_usuario()

    if not id_usuario:
        return jsonify({
            "mensaje":
                "Usuario no válido."
        }), 401

    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    consulta = (
        Notificacion.query
        .filter_by(
            id_usuario=id_usuario
        )
    )

    if id_ciclo:
        consulta = consulta.filter(
            db.or_(
                Notificacion.id_ciclo
                == id_ciclo,

                Notificacion.id_ciclo
                .is_(None)
            )
        )

    notificaciones = (
        consulta
        .order_by(
            Notificacion.leida.asc(),
            Notificacion.fecha_creacion.desc(),
            Notificacion.id_notificacion.desc(),
        )
        .limit(50)
        .all()
    )

    no_leidas = (
        consulta
        .filter_by(
            leida=False
        )
        .count()
    )

    return jsonify({
        "notificaciones": [
            item.to_dict()
            for item in notificaciones
        ],

        "no_leidas":
            no_leidas,
    }), 200


@notificaciones_bp.patch(
    "/<int:id_notificacion>/leer"
)
@permission_required("documentos.ver")
def marcar_como_leida(
    id_notificacion
):
    id_usuario = obtener_id_usuario()

    if not id_usuario:
        return jsonify({
            "mensaje":
                "Usuario no válido."
        }), 401

    notificacion = (
        Notificacion.query
        .filter_by(
            id_notificacion=
                id_notificacion,

            id_usuario=
                id_usuario,
        )
        .first()
    )

    if not notificacion:
        return jsonify({
            "mensaje":
                "La notificación no existe."
        }), 404

    if not notificacion.leida:
        notificacion.leida = True

        notificacion.fecha_lectura = (
            datetime.now(
                timezone.utc
            )
        )

        db.session.commit()

    return jsonify({
        "mensaje":
            "Notificación marcada como leída.",

        "notificacion":
            notificacion.to_dict(),
    }), 200


@notificaciones_bp.patch(
    "/leer-todas"
)
@permission_required("documentos.ver")
def marcar_todas_como_leidas():
    id_usuario = obtener_id_usuario()

    if not id_usuario:
        return jsonify({
            "mensaje":
                "Usuario no válido."
        }), 401

    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    consulta = (
        Notificacion.query
        .filter_by(
            id_usuario=id_usuario,
            leida=False,
        )
    )

    if id_ciclo:
        consulta = consulta.filter(
            db.or_(
                Notificacion.id_ciclo
                == id_ciclo,

                Notificacion.id_ciclo
                .is_(None)
            )
        )

    pendientes = consulta.all()

    ahora = datetime.now(
        timezone.utc
    )

    for notificacion in pendientes:
        notificacion.leida = True
        notificacion.fecha_lectura = ahora

    db.session.commit()

    return jsonify({
        "mensaje":
            "Todas las notificaciones fueron marcadas como leídas.",

        "actualizadas":
            len(pendientes),
    }), 200