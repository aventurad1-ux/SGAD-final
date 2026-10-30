from datetime import datetime, time

from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_

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
            request.args.get(
                "pagina",
                1,
                type=int
            ),
            1
        )

        limite = min(
            max(
                request.args.get(
                    "limite",
                    20,
                    type=int
                ),
                1
            ),
            100
        )

        busqueda = (
            request.args.get(
                "busqueda",
                ""
            ).strip()
        )

        id_usuario = request.args.get(
            "id_usuario",
            type=int
        )

        fecha_desde = (
            request.args.get(
                "fecha_desde",
                ""
            ).strip()
        )

        fecha_hasta = (
            request.args.get(
                "fecha_hasta",
                ""
            ).strip()
        )

        consulta = Bitacora.query

        # ==========================================
        # BÚSQUEDA GENERAL
        # ==========================================

        if busqueda:
            patron = f"%{busqueda}%"

            consulta = consulta.filter(
                or_(
                    Bitacora.accion.ilike(
                        patron
                    ),
                    Bitacora.modulo.ilike(
                        patron
                    ),
                    Bitacora.registro.ilike(
                        patron
                    ),
                    Bitacora.descripcion.ilike(
                        patron
                    )
                )
            )

        # ==========================================
        # FILTRO POR USUARIO
        # ==========================================

        if id_usuario:
            consulta = consulta.filter(
                Bitacora.id_usuario
                == id_usuario
            )

        # ==========================================
        # FECHA DESDE
        # ==========================================

        if fecha_desde:
            try:
                fecha_inicio = (
                    datetime.strptime(
                        fecha_desde,
                        "%Y-%m-%d"
                    )
                )

                consulta = consulta.filter(
                    Bitacora.fecha_hora
                    >= fecha_inicio
                )

            except ValueError:
                return jsonify({
                    "mensaje":
                        "La fecha inicial no es válida."
                }), 400

        # ==========================================
        # FECHA HASTA
        # ==========================================

        if fecha_hasta:
            try:
                fecha_fin = (
                    datetime.combine(
                        datetime.strptime(
                            fecha_hasta,
                            "%Y-%m-%d"
                        ).date(),
                        time.max
                    )
                )

                consulta = consulta.filter(
                    Bitacora.fecha_hora
                    <= fecha_fin
                )

            except ValueError:
                return jsonify({
                    "mensaje":
                        "La fecha final no es válida."
                }), 400

        resultado = (
            consulta
            .order_by(
                Bitacora.fecha_hora.desc(),
                Bitacora.id_bitacora.desc()
            )
            .paginate(
                page=pagina,
                per_page=limite,
                error_out=False
            )
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
                "id_bitacora":
                    registro.id_bitacora,

                "id_usuario":
                    registro.id_usuario,

                "usuario":
                    nombre_usuario,

                "accion":
                    registro.accion,

                "modulo":
                    registro.modulo,

                "registro":
                    registro.registro,

                "descripcion":
                    registro.descripcion,

                "fecha_hora":
                    (
                        registro.fecha_hora.isoformat() + "Z"
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

    except Exception as error:
        print(
            "ERROR CONSULTANDO BITÁCORA:",
            error
        )

        return jsonify({
            "mensaje":
                "Error al consultar la bitácora"
        }), 500


@bitacora_bp.route(
    "/usuarios",
    methods=["GET"]
)
@permission_required("auditoria.ver")
def listar_usuarios_bitacora():
    try:
        usuarios = (
            Usuario.query
            .filter_by(activo=True)
            .order_by(
                Usuario.nombres.asc(),
                Usuario.apellidos.asc()
            )
            .all()
        )

        resultado = []

        for usuario in usuarios:
            resultado.append({
                "id_usuario":
                    usuario.id_usuario,

                "nombre":
                    (
                        f"{usuario.nombres} "
                        f"{usuario.apellidos}"
                    )
            })

        return jsonify({
            "usuarios": resultado
        }), 200

    except Exception as error:
        print(
            "ERROR CARGANDO USUARIOS:",
            error
        )

        return jsonify({
            "mensaje":
                "No fue posible cargar los usuarios."
        }), 500