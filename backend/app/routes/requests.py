from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import (
    Solicitud,
    SolicitudDestinatario,
    SolicitudRequisito,
    Entrega,
    VersionEntrega,
    Usuario,
    CicloEscolar,
)
from app.utils.permissions import permission_required


requests_bp = Blueprint(
    "requests",
    __name__,
    url_prefix="/api/directora/solicitudes",
)


# =========================================================
# HELPERS
# =========================================================

FORMATOS_LEGIBLES = {
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
    "image/png": "PNG/JPG",
    "image/jpeg": "PNG/JPG",
    "image/jpg": "PNG/JPG",
    "PDF": "PDF",
    "DOCX": "DOCX",
    "XLSX": "XLSX",
    "PNG": "PNG/JPG",
    "JPG": "PNG/JPG",
    "PNG/JPG": "PNG/JPG",
}


def nombre_usuario(usuario):
    if not usuario:
        return "—"

    return f"{usuario.nombres or ''} {usuario.apellidos or ''}".strip()


def convertir_formatos(valor):
    if not valor:
        return []

    resultado = []

    for item in str(valor).split(","):
        item = item.strip()

        if not item:
            continue

        nombre = FORMATOS_LEGIBLES.get(item, item)

        if nombre not in resultado:
            resultado.append(nombre)

    return resultado


def obtener_formatos_solicitud(id_solicitud):
    requisitos = (
        SolicitudRequisito.query
        .filter_by(
            id_solicitud=id_solicitud,
            activo=True,
        )
        .order_by(SolicitudRequisito.orden.asc())
        .all()
    )

    formatos = []

    for requisito in requisitos:
        for formato in convertir_formatos(
            requisito.formato_permitido
        ):
            if formato not in formatos:
                formatos.append(formato)

    return formatos


def obtener_destinatarios(id_solicitud):
    return (
        SolicitudDestinatario.query
        .filter_by(id_solicitud=id_solicitud)
        .order_by(
            SolicitudDestinatario.id_destinatario.asc()
        )
        .all()
    )


def obtener_entrega_destinatario(destinatario):
    """
    Devuelve una entrega si el docente ya realizó
    una entrega alguna vez.

    Una corrección solicitada sigue contando como
    cumplimiento porque el docente sí entregó.
    """
    entregas = (
        Entrega.query
        .filter_by(
            id_destinatario=destinatario.id_destinatario
        )
        .order_by(Entrega.id_entrega.desc())
        .all()
    )

    for entrega in entregas:
        if (
            entrega.fecha_primera_entrega
            or entrega.estado in {
                "entregado",
                "en_revision",
                "correccion_solicitada",
                "aprobado",
                "rechazado",
            }
        ):
            return entrega

    return None


def obtener_ultima_version(entrega):
    if not entrega:
        return None

    return (
        VersionEntrega.query
        .filter_by(id_entrega=entrega.id_entrega)
        .order_by(VersionEntrega.numero_version.desc())
        .first()
    )


def serializar_solicitud(solicitud):
    destinatarios = obtener_destinatarios(
        solicitud.id_solicitud
    )

    total_destinatarios = len(destinatarios)

    total_entregados = 0

    for destinatario in destinatarios:
        if obtener_entrega_destinatario(destinatario):
            total_entregados += 1

    porcentaje = 0

    if total_destinatarios:
        porcentaje = round(
            total_entregados
            * 100
            / total_destinatarios
        )

    return {
        "id_solicitud": solicitud.id_solicitud,
        "titulo": solicitud.titulo,
        "descripcion": solicitud.descripcion,
        "categoria": (
            solicitud.categoria
            or "Evidencias docentes"
        ),
        "id_ciclo": solicitud.id_ciclo,
        "fecha_publicacion": (
            solicitud.fecha_publicacion.isoformat()
            if solicitud.fecha_publicacion
            else None
        ),
        "fecha_limite": (
            solicitud.fecha_limite.isoformat()
            if solicitud.fecha_limite
            else None
        ),
        "prioridad": solicitud.prioridad,
        "estado": solicitud.estado,
        "formatos_permitidos": (
            obtener_formatos_solicitud(
                solicitud.id_solicitud
            )
        ),
        "total_destinatarios": total_destinatarios,
        "total_entregados": total_entregados,
        "porcentaje_cumplimiento": porcentaje,
    }


# =========================================================
# LISTAR
# =========================================================

@requests_bp.get("")
@permission_required("documentos.ver")
def listar_solicitudes():
    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    consulta = Solicitud.query

    if id_ciclo:
        consulta = consulta.filter_by(
            id_ciclo=id_ciclo
        )

    solicitudes = (
        consulta
        .order_by(
            Solicitud.fecha_publicacion.desc(),
            Solicitud.id_solicitud.desc(),
        )
        .all()
    )

    return jsonify({
        "solicitudes": [
            serializar_solicitud(item)
            for item in solicitudes
        ]
    }), 200


# =========================================================
# CATÁLOGOS
# =========================================================

@requests_bp.get("/catalogos")
@permission_required("documentos.ver")
def obtener_catalogos():
    ciclos = (
        CicloEscolar.query
        .order_by(CicloEscolar.anio.desc())
        .all()
    )

    usuarios = (
        Usuario.query
        .filter_by(activo=True)
        .all()
    )

    docentes = []

    for usuario in usuarios:
        if (
            usuario.rol
            and usuario.rol.nombre == "Docente"
        ):
            docentes.append({
                "id_usuario": usuario.id_usuario,
                "nombre": nombre_usuario(usuario),
                "correo": usuario.correo,
                # Todavía no tenemos secciones reales
                # relacionadas aquí.
                "alcance": "Sin sección",
            })

    return jsonify({
        "ciclos": [
            {
                "id_ciclo": ciclo.id_ciclo,
                "anio": ciclo.anio,
                "estado": ciclo.estado,
            }
            for ciclo in ciclos
        ],
        "docentes": docentes,
    }), 200


# =========================================================
# CREAR
# =========================================================

@requests_bp.post("")
@permission_required("documentos.ver")
def crear_solicitud():
    data = request.get_json() or {}

    titulo = str(
        data.get("titulo", "")
    ).strip()

    descripcion = str(
        data.get("descripcion", "")
    ).strip()

    categoria = str(
        data.get(
            "categoria",
            "Evidencias docentes",
        )
    ).strip()

    prioridad = str(
        data.get(
            "prioridad",
            "normal",
        )
    ).lower()

    fecha_limite = data.get(
        "fecha_limite"
    )

    id_ciclo = data.get(
        "id_ciclo"
    )

    destinatarios = data.get(
        "destinatarios",
        [],
    )

    formatos = data.get(
        "formatos",
        [],
    )

    if not titulo:
        return jsonify({
            "mensaje":
                "El título es obligatorio."
        }), 400

    if not descripcion:
        return jsonify({
            "mensaje":
                "La descripción es obligatoria."
        }), 400

    if not fecha_limite:
        return jsonify({
            "mensaje":
                "La fecha límite es obligatoria."
        }), 400

    if not id_ciclo:
        return jsonify({
            "mensaje":
                "Debe seleccionar un ciclo escolar."
        }), 400

    if not destinatarios:
        return jsonify({
            "mensaje":
                "Seleccione al menos un docente."
        }), 400

    if not formatos:
        return jsonify({
            "mensaje":
                "Seleccione al menos un formato permitido."
        }), 400

    if prioridad not in {
        "normal",
        "alta",
    }:
        return jsonify({
            "mensaje":
                "La prioridad no es válida."
        }), 400

    ciclo = db.session.get(
        CicloEscolar,
        int(id_ciclo),
    )

    if not ciclo:
        return jsonify({
            "mensaje":
                "El ciclo escolar no existe."
        }), 404

    if ciclo.estado != "activo":
        return jsonify({
            "mensaje":
                "No puede crear solicitudes en un ciclo histórico."
        }), 400

    try:
        fecha_limite_dt = datetime.fromisoformat(
            str(fecha_limite).replace(
                "Z",
                "+00:00",
            )
        )
    except (TypeError, ValueError):
        return jsonify({
            "mensaje":
                "La fecha límite no es válida."
        }), 400

    ahora = datetime.now(
        timezone.utc
    )

    # Si viene sin timezone, lo dejamos UTC.
    if fecha_limite_dt.tzinfo is None:
        fecha_limite_dt = (
            fecha_limite_dt.replace(
                tzinfo=timezone.utc
            )
        )

    try:
        id_usuario = int(
            get_jwt_identity()
        )

        solicitud = Solicitud(
            titulo=titulo,
            descripcion=descripcion,
            categoria=categoria,
            id_usuario_creador=id_usuario,
            id_ciclo=ciclo.id_ciclo,
            fecha_publicacion=ahora,
            fecha_limite=fecha_limite_dt,
            prioridad=prioridad,
            estado="publicada",
            fecha_actualizacion=ahora,
        )

        db.session.add(solicitud)
        db.session.flush()

        ids_docentes = set()

        for valor in destinatarios:
            id_docente = int(valor)

            if id_docente in ids_docentes:
                continue

            docente = db.session.get(
                Usuario,
                id_docente,
            )

            if not docente:
                raise ValueError(
                    "Uno de los docentes seleccionados no existe."
                )

            if (
                not docente.activo
                or not docente.rol
                or docente.rol.nombre != "Docente"
            ):
                raise ValueError(
                    f"{nombre_usuario(docente)} no es un docente activo."
                )

            ids_docentes.add(id_docente)

            db.session.add(
                SolicitudDestinatario(
                    id_solicitud=solicitud.id_solicitud,
                    id_docente=id_docente,
                    estado="pendiente",
                )
            )

        formatos_limpios = []

        for formato in formatos:
            valor = str(formato).strip().upper()

            if valor in {
                "PDF",
                "DOCX",
                "XLSX",
                "PNG",
                "PNG/JPG",
            }:
                if valor not in formatos_limpios:
                    formatos_limpios.append(valor)

        if not formatos_limpios:
            raise ValueError(
                "No existe ningún formato permitido válido."
            )

        db.session.add(
            SolicitudRequisito(
                id_solicitud=solicitud.id_solicitud,
                nombre_documento=titulo,
                descripcion=descripcion,
                obligatorio=True,
                formato_permitido=",".join(
                    formatos_limpios
                ),
                orden=1,
                activo=True,
            )
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Solicitud enviada a los docentes.",
            "solicitud":
                serializar_solicitud(
                    solicitud
                ),
        }), 201

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            "mensaje": str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CREAR SOLICITUD:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible crear la solicitud."
        }), 500


# =========================================================
# CUMPLIMIENTO
# =========================================================

@requests_bp.get(
    "/<int:id_solicitud>/cumplimiento"
)
@permission_required("documentos.ver")
def obtener_cumplimiento(
    id_solicitud
):
    solicitud = db.session.get(
        Solicitud,
        id_solicitud,
    )

    if not solicitud:
        return jsonify({
            "mensaje":
                "La solicitud no existe."
        }), 404

    ahora = datetime.now(
        timezone.utc
    )

    fecha_limite = (
        solicitud.fecha_limite
    )

    if (
        fecha_limite
        and fecha_limite.tzinfo is None
    ):
        fecha_limite = fecha_limite.replace(
            tzinfo=timezone.utc
        )

    filas = []

    for destinatario in obtener_destinatarios(
        id_solicitud
    ):
        docente = db.session.get(
            Usuario,
            destinatario.id_docente,
        )

        entrega = (
            obtener_entrega_destinatario(
                destinatario
            )
        )

        ultima_version = (
            obtener_ultima_version(
                entrega
            )
        )

        if entrega:
            estado = entrega.estado

            fecha = (
                entrega.fecha_actualizacion
                or entrega.fecha_primera_entrega
            )

            id_entrega = (
                entrega.id_entrega
            )

            archivo = (
                ultima_version.nombre_archivo
                if ultima_version
                else None
            )

        else:
            vencida = (
                fecha_limite is not None
                and ahora > fecha_limite
            )

            estado = (
                "vencido"
                if vencida
                else "pendiente"
            )

            fecha = None
            id_entrega = None
            archivo = None

        filas.append({
            "id_destinatario":
                destinatario.id_destinatario,

            "id_docente":
                docente.id_usuario
                if docente
                else None,

            "docente":
                nombre_usuario(docente),

            # Hasta que Ciclo escolar tenga
            # las secciones reales conectadas.
            "alcance":
                "Sin sección",

            "estado":
                estado,

            "fecha":
                fecha.isoformat()
                if fecha
                else None,

            "id_entrega":
                id_entrega,

            "archivo":
                archivo,
        })

    return jsonify({
        "solicitud":
            serializar_solicitud(
                solicitud
            ),
        "cumplimiento":
            filas,
    }), 200


# =========================================================
# CERRAR
# =========================================================

@requests_bp.post(
    "/<int:id_solicitud>/cerrar"
)
@permission_required("documentos.ver")
def cerrar_solicitud(
    id_solicitud
):
    solicitud = db.session.get(
        Solicitud,
        id_solicitud,
    )

    if not solicitud:
        return jsonify({
            "mensaje":
                "La solicitud no existe."
        }), 404

    if solicitud.estado != "publicada":
        return jsonify({
            "mensaje":
                "Solo puede cerrar una solicitud vigente."
        }), 400

    ciclo = db.session.get(
        CicloEscolar,
        solicitud.id_ciclo,
    )

    if (
        not ciclo
        or ciclo.estado != "activo"
    ):
        return jsonify({
            "mensaje":
                "La solicitud pertenece a un ciclo histórico."
        }), 400

    solicitud.estado = "cerrada"

    solicitud.fecha_actualizacion = (
        datetime.now(
            timezone.utc
        )
    )

    db.session.commit()

    return jsonify({
        "mensaje":
            "Solicitud cerrada correctamente.",
        "solicitud":
            serializar_solicitud(
                solicitud
            ),
    }), 200


# =========================================================
# REABRIR
# =========================================================

@requests_bp.post(
    "/<int:id_solicitud>/reabrir"
)
@permission_required("documentos.ver")
def reabrir_solicitud(
    id_solicitud
):
    solicitud = db.session.get(
        Solicitud,
        id_solicitud,
    )

    if not solicitud:
        return jsonify({
            "mensaje":
                "La solicitud no existe."
        }), 404

    if solicitud.estado != "cerrada":
        return jsonify({
            "mensaje":
                "Solo puede reabrir una solicitud cerrada."
        }), 400

    ciclo = db.session.get(
        CicloEscolar,
        solicitud.id_ciclo,
    )

    if (
        not ciclo
        or ciclo.estado != "activo"
    ):
        return jsonify({
            "mensaje":
                "No puede reabrir solicitudes de un ciclo histórico."
        }), 400

    data = request.get_json() or {}

    nueva_fecha = data.get(
        "fecha_limite"
    )

    if not nueva_fecha:
        return jsonify({
            "mensaje":
                "Indique la nueva fecha límite."
        }), 400

    try:
        nueva_fecha_dt = (
            datetime.fromisoformat(
                str(nueva_fecha).replace(
                    "Z",
                    "+00:00",
                )
            )
        )
    except (TypeError, ValueError):
        return jsonify({
            "mensaje":
                "La nueva fecha límite no es válida."
        }), 400

    if nueva_fecha_dt.tzinfo is None:
        nueva_fecha_dt = (
            nueva_fecha_dt.replace(
                tzinfo=timezone.utc
            )
        )

    ahora = datetime.now(
        timezone.utc
    )

    if nueva_fecha_dt.date() < ahora.date():
        return jsonify({
            "mensaje":
                "La nueva fecha límite no puede estar en el pasado."
        }), 400

    solicitud.estado = "publicada"
    solicitud.fecha_limite = nueva_fecha_dt
    solicitud.fecha_actualizacion = ahora

    db.session.commit()

    return jsonify({
        "mensaje":
            "Solicitud reabierta correctamente.",
        "solicitud":
            serializar_solicitud(
                solicitud
            ),
    }), 200