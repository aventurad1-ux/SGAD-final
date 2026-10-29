
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.models.bitacora import Bitacora
from app.models.usuario import Usuario
from app.utils.permissions import permission_required


bitacora_bp = Blueprint(
    "bitacora",
    __name__,
    url_prefix="/api/bitacora"
)


@bitacora_bp.route("", methods=["GET"])
@permission_required("auditoria.ver")
def listar_bitacora():
    try:
        pagina = max(
            request.args.get("pagina", 1, type=int),
            1
        )

        limite = min(
            max(request.args.get("limite", 20, type=int), 1),
            100
        )

        modulo = request.args.get("modulo", "").strip()
        accion = request.args.get("accion", "").strip()
        usuario = request.args.get("usuario", "").strip()

        consulta = Bitacora.query

        if modulo:
            consulta = consulta.filter(
                Bitacora.modulo.ilike(f"%{modulo}%")
            )

        if accion:
            consulta = consulta.filter(
                Bitacora.accion.ilike(f"%{accion}%")
            )

        if usuario:
            consulta = consulta.join(
                Usuario,
                Bitacora.id_usuario == Usuario.id_usuario
            ).filter(
                func.concat(
                    Usuario.nombres,
                    " ",
                    Usuario.apellidos
                ).ilike(f"%{usuario}%")
            )

        resultado = consulta.order_by(
            Bitacora.fecha_hora.desc(),
            Bitacora.id_bitacora.desc()
        ).paginate(
            page=pagina,
            per_page=limite,
            error_out=False
        )

        registros = []

        for registro in resultado.items:
            nombre_usuario = None

            if registro.usuario:
                nombre_usuario = (
                    f"{registro.usuario.nombres} "
                    f"{registro.usuario.apellidos}"
                )

            registros.append({
                "id_bitacora": registro.id_bitacora,
                "id_usuario": registro.id_usuario,
                "usuario": nombre_usuario,
                "accion": registro.accion,
                "modulo": registro.modulo,
                "descripcion": registro.descripcion,
                "fecha_hora": (
                    registro.fecha_hora.isoformat()
                    if registro.fecha_hora
                    else None
                )
            })

        return jsonify({
            "registros": registros,
            "total": resultado.total,
            "pagina": pagina,
            "paginas": resultado.pages
        }), 200

    except Exception:
        return jsonify({
            "mensaje": "Error al consultar la bitácora"
        }), 500
