from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import hashlib

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_file,
)
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Entrega,
    RevisionEntrega,
    Solicitud,
    SolicitudDestinatario,
    SolicitudRequisito,
    VersionEntrega,
)
from app.utils.permissions import permission_required


docente_solicitudes_bp = Blueprint(
    "docente_solicitudes",
    __name__,
    url_prefix="/api/docente/solicitudes",
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

EXTENSIONES_FORMATO = {
    "PDF": {"pdf"},
    "DOCX": {"docx"},
    "XLSX": {"xlsx"},
    "PNG": {"png"},
    "JPG": {"jpg", "jpeg"},
    "JPEG": {"jpg", "jpeg"},
    "PNG/JPG": {"png", "jpg", "jpeg"},
}

MIME_POR_EXTENSION = {
    "pdf": "application/pdf",
    "docx":
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document",
    "xlsx":
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}


# =========================================================
# UTILIDADES
# =========================================================

def ahora_utc():
    return datetime.now(timezone.utc)


def backend_root():
    """
    current_app.root_path apunta a backend/app.
    Subimos un nivel para llegar a backend.
    """
    return Path(current_app.root_path).parent


def storage_root():
    ruta = (
        backend_root()
        / "storage"
        / "entregas"
    )

    ruta.mkdir(
        parents=True,
        exist_ok=True,
    )

    return ruta


def normalizar_fecha(fecha):
    if not fecha:
        return None

    if fecha.tzinfo is None:
        return fecha.replace(
            tzinfo=timezone.utc
        )

    return fecha


def nombre_usuario(usuario):
    if not usuario:
        return "—"

    return (
        f"{usuario.nombres or ''} "
        f"{usuario.apellidos or ''}"
    ).strip()


def formatos_requisito(requisito):
    if (
        not requisito
        or not requisito.formato_permitido
    ):
        return []

    resultado = []

    for item in requisito.formato_permitido.split(","):
        formato = item.strip().upper()

        if formato and formato not in resultado:
            resultado.append(formato)

    return resultado


def extensiones_permitidas(requisito):
    resultado = set()

    for formato in formatos_requisito(
        requisito
    ):
        resultado.update(
            EXTENSIONES_FORMATO.get(
                formato,
                set(),
            )
        )

    return resultado


def obtener_destinatario_docente(
    id_destinatario,
):
    try:
        id_docente = int(
            get_jwt_identity()
        )
    except (TypeError, ValueError):
        return None

    return (
        SolicitudDestinatario.query
        .filter_by(
            id_destinatario=id_destinatario,
            id_docente=id_docente,
        )
        .first()
    )


def obtener_entrega(
    destinatario,
    requisito,
):
    return (
        Entrega.query
        .filter_by(
            id_destinatario=(
                destinatario.id_destinatario
            ),
            id_requisito_solicitud=(
                requisito.id_requisito_solicitud
            ),
        )
        .first()
    )


def obtener_ultima_version(entrega):
    if not entrega:
        return None

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


def serializar_revision(revision):
    return {
        "id_revision":
            revision.id_revision,

        "resultado":
            revision.resultado,

        "observaciones":
            revision.observaciones,

        "fecha_revision": (
            revision.fecha_revision.isoformat()
            if revision.fecha_revision
            else None
        ),

        "revisor":
            nombre_usuario(
                revision.revisor
            ),
    }


def serializar_version(version):
    revisiones = (
        RevisionEntrega.query
        .filter_by(
            id_version_entrega=(
                version.id_version_entrega
            )
        )
        .order_by(
            RevisionEntrega.fecha_revision.desc()
        )
        .all()
    )

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

        "comentario":
            version.comentario,

        "fecha_subida": (
            version.fecha_subida.isoformat()
            if version.fecha_subida
            else None
        ),

        "usuario":
            nombre_usuario(
                version.usuario
            ),

        "revisiones": [
            serializar_revision(item)
            for item in revisiones
        ],
    }


def serializar_requisito(
    requisito,
    destinatario,
):
    entrega = obtener_entrega(
        destinatario,
        requisito,
    )

    versiones = []

    if entrega:
        versiones = (
            VersionEntrega.query
            .filter_by(
                id_entrega=entrega.id_entrega
            )
            .order_by(
                VersionEntrega.numero_version.desc()
            )
            .all()
        )

    ultima_version = (
        versiones[0]
        if versiones
        else None
    )

    return {
        "id_requisito_solicitud":
            requisito.id_requisito_solicitud,

        "nombre_documento":
            requisito.nombre_documento,

        "descripcion":
            requisito.descripcion,

        "obligatorio":
            requisito.obligatorio,

        "formatos_permitidos":
            formatos_requisito(
                requisito
            ),

        "estado_entrega": (
            entrega.estado
            if entrega
            else "pendiente"
        ),

        "id_entrega": (
            entrega.id_entrega
            if entrega
            else None
        ),

        "observaciones": (
            entrega.observaciones
            if entrega
            else None
        ),

        "fecha_primera_entrega": (
            entrega.fecha_primera_entrega.isoformat()
            if (
                entrega
                and entrega.fecha_primera_entrega
            )
            else None
        ),

        "fecha_actualizacion": (
            entrega.fecha_actualizacion.isoformat()
            if (
                entrega
                and entrega.fecha_actualizacion
            )
            else None
        ),

        "ultima_version": (
            serializar_version(
                ultima_version
            )
            if ultima_version
            else None
        ),

        "versiones": [
            serializar_version(item)
            for item in versiones
        ],
    }


def obtener_estado_general(
    solicitud,
    destinatario,
):
    """
    Estado mostrado al Docente.

    Importante:
    - Una solicitud vencida sigue permitiendo entregar.
    - Una solicitud cerrada es solo consulta.
    """

    if solicitud.estado == "cerrada":
        return "cerrado"

    requisitos = (
        SolicitudRequisito.query
        .filter_by(
            id_solicitud=solicitud.id_solicitud,
            activo=True,
        )
        .order_by(
            SolicitudRequisito.orden.asc()
        )
        .all()
    )

    entregas = []

    for requisito in requisitos:
        entrega = obtener_entrega(
            destinatario,
            requisito,
        )

        if entrega:
            entregas.append(entrega)

    # -----------------------------------------
    # CORRECCIÓN SOLICITADA
    # -----------------------------------------

    if any(
        item.estado
        == "correccion_solicitada"
        for item in entregas
    ):
        return "correccion_solicitada"

    # -----------------------------------------
    # RECHAZADO
    # -----------------------------------------

    if any(
        item.estado == "rechazado"
        for item in entregas
    ):
        return "rechazado"

    # -----------------------------------------
    # TODOS APROBADOS
    # -----------------------------------------

    obligatorios = [
        item
        for item in requisitos
        if item.obligatorio
    ]

    if obligatorios:
        aprobados = 0

        for requisito in obligatorios:
            entrega = obtener_entrega(
                destinatario,
                requisito,
            )

            if (
                entrega
                and entrega.estado == "aprobado"
            ):
                aprobados += 1

        if aprobados == len(obligatorios):
            return "aprobado"

    # -----------------------------------------
    # EXISTE ENTREGA EN REVISIÓN
    # -----------------------------------------

    if any(
        item.estado in {
            "entregado",
            "en_revision",
        }
        for item in entregas
    ):
        return "en_revision"

    # -----------------------------------------
    # PENDIENTE / VENCIDO
    # -----------------------------------------

    fecha_limite = normalizar_fecha(
        solicitud.fecha_limite
    )

    if (
        fecha_limite
        and ahora_utc() > fecha_limite
    ):
        return "vencido"

    return "pendiente"


def obtener_accion(
    solicitud,
    estado,
):
    if solicitud.estado == "cerrada":
        return "ver_solicitud"

    if estado in {
        "pendiente",
        "vencido",
        "correccion_solicitada",
    }:
        return "entregar"

    if estado in {
        "aprobado",
        "en_revision",
        "rechazado",
    }:
        return "ver_entrega"

    return "ver_solicitud"


def serializar_solicitud_docente(
    destinatario,
    detalle=False,
):
    solicitud = destinatario.solicitud

    estado = obtener_estado_general(
        solicitud,
        destinatario,
    )

    requisitos = (
        SolicitudRequisito.query
        .filter_by(
            id_solicitud=solicitud.id_solicitud,
            activo=True,
        )
        .order_by(
            SolicitudRequisito.orden.asc()
        )
        .all()
    )

    formatos = []

    for requisito in requisitos:
        for formato in formatos_requisito(
            requisito
        ):
            if formato not in formatos:
                formatos.append(formato)

    resultado = {
        "id_destinatario":
            destinatario.id_destinatario,

        "id_solicitud":
            solicitud.id_solicitud,

        "titulo":
            solicitud.titulo,

        "descripcion":
            solicitud.descripcion,

        "categoria":
            solicitud.categoria,

        "id_ciclo":
            solicitud.id_ciclo,

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

        "prioridad":
            solicitud.prioridad,

        "estado_solicitud":
            solicitud.estado,

        "estado":
            estado,

        "accion":
            obtener_accion(
                solicitud,
                estado,
            ),

        "formatos_permitidos":
            formatos,

        "fecha_asignacion": (
            destinatario.fecha_asignacion.isoformat()
            if destinatario.fecha_asignacion
            else None
        ),

        "fecha_lectura": (
            destinatario.fecha_lectura.isoformat()
            if destinatario.fecha_lectura
            else None
        ),
    }

    if detalle:
        resultado["requisitos"] = [
            serializar_requisito(
                requisito,
                destinatario,
            )
            for requisito in requisitos
        ]

    return resultado


# =========================================================
# LISTAR MIS SOLICITUDES
# =========================================================

@docente_solicitudes_bp.get("")
@permission_required("solicitudes.ver")
def listar_mis_solicitudes():
    try:
        id_docente = int(
            get_jwt_identity()
        )
    except (TypeError, ValueError):
        return jsonify({
            "mensaje":
                "Usuario no válido."
        }), 401

    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    consulta = (
        SolicitudDestinatario.query
        .join(
            Solicitud,
            Solicitud.id_solicitud
            == SolicitudDestinatario.id_solicitud,
        )
        .filter(
            SolicitudDestinatario.id_docente
            == id_docente
        )
    )

    if id_ciclo:
        consulta = consulta.filter(
            Solicitud.id_ciclo
            == id_ciclo
        )

    destinatarios = (
        consulta
        .order_by(
            Solicitud.fecha_limite.asc(),
            Solicitud.id_solicitud.desc(),
        )
        .all()
    )

    solicitudes = [
        serializar_solicitud_docente(
            item
        )
        for item in destinatarios
    ]

    # Las que requieren atención primero.
    prioridad_estado = {
        "correccion_solicitada": 0,
        "vencido": 1,
        "pendiente": 2,
        "en_revision": 3,
        "aprobado": 4,
        "rechazado": 5,
        "cerrado": 6,
    }

    solicitudes.sort(
        key=lambda item: (
            prioridad_estado.get(
                item["estado"],
                99,
            ),
            item["fecha_limite"] or "",
        )
    )

    pendientes = sum(
        1
        for item in solicitudes
        if item["estado"] in {
            "pendiente",
            "vencido",
            "correccion_solicitada",
        }
    )

    return jsonify({
        "solicitudes":
            solicitudes,

        "total":
            len(solicitudes),

        "pendientes":
            pendientes,
    }), 200


# =========================================================
# VER SOLICITUD
# =========================================================

@docente_solicitudes_bp.get(
    "/<int:id_destinatario>"
)
@permission_required("solicitudes.ver")
def ver_mi_solicitud(
    id_destinatario,
):
    destinatario = (
        obtener_destinatario_docente(
            id_destinatario
        )
    )

    if not destinatario:
        return jsonify({
            "mensaje":
                "La solicitud no existe o no está asignada a este docente."
        }), 404

    # Registrar lectura sin cambiar el estado visual.
    if not destinatario.fecha_lectura:
        destinatario.fecha_lectura = (
            ahora_utc()
        )

        db.session.commit()

    return jsonify({
        "solicitud":
            serializar_solicitud_docente(
                destinatario,
                detalle=True,
            )
    }), 200


# =========================================================
# REALIZAR ENTREGA / CORRECCIÓN
# =========================================================

@docente_solicitudes_bp.post(
    "/<int:id_destinatario>"
    "/requisitos/<int:id_requisito>/entregar"
)
@permission_required("solicitudes.entregar")
def realizar_entrega(
    id_destinatario,
    id_requisito,
):
    destinatario = (
        obtener_destinatario_docente(
            id_destinatario
        )
    )

    if not destinatario:
        return jsonify({
            "mensaje":
                "La solicitud no existe o no está asignada a este docente."
        }), 404

    solicitud = destinatario.solicitud

    if solicitud.estado == "cerrada":
        return jsonify({
            "mensaje":
                "La solicitud está cerrada y ya no admite entregas."
        }), 400

    requisito = (
        SolicitudRequisito.query
        .filter_by(
            id_requisito_solicitud=id_requisito,
            id_solicitud=solicitud.id_solicitud,
            activo=True,
        )
        .first()
    )

    if not requisito:
        return jsonify({
            "mensaje":
                "El requisito no pertenece a esta solicitud."
        }), 404

    archivo = request.files.get(
        "archivo"
    )

    observaciones = str(
        request.form.get(
            "observaciones",
            ""
        )
    ).strip()

    if not archivo:
        return jsonify({
            "mensaje":
                "Seleccione un archivo."
        }), 400

    if not archivo.filename:
        return jsonify({
            "mensaje":
                "Seleccione un archivo válido."
        }), 400

    nombre_original = secure_filename(
        archivo.filename
    )

    if "." not in nombre_original:
        return jsonify({
            "mensaje":
                "El archivo no tiene una extensión válida."
        }), 400

    extension = (
        nombre_original
        .rsplit(".", 1)[1]
        .lower()
    )

    permitidas = extensiones_permitidas(
        requisito
    )

    if (
        permitidas
        and extension not in permitidas
    ):
        return jsonify({
            "mensaje": (
                "Formato no permitido. "
                f"Formatos aceptados: "
                f"{', '.join(formatos_requisito(requisito))}."
            )
        }), 400

    contenido = archivo.read()

    if not contenido:
        return jsonify({
            "mensaje":
                "El archivo está vacío."
        }), 400

    if len(contenido) > MAX_FILE_SIZE:
        return jsonify({
            "mensaje":
                "El archivo supera el límite de 10 MB."
        }), 400

    entrega = obtener_entrega(
        destinatario,
        requisito,
    )

    # -----------------------------------------
    # NO PERMITIR SOBREESCRIBIR MIENTRAS
    # DIRECCIÓN AÚN REVISA
    # -----------------------------------------

    if (
        entrega
        and entrega.estado in {
            "entregado",
            "en_revision",
            "aprobado",
        }
    ):
        return jsonify({
            "mensaje": (
                "Esta entrega no admite una nueva versión "
                "en su estado actual."
            )
        }), 400

    if (
        entrega
        and entrega.estado == "rechazado"
    ):
        return jsonify({
            "mensaje":
                "La entrega fue rechazada y no admite nuevas versiones."
        }), 400

    try:
        ahora = ahora_utc()

        if not entrega:
            entrega = Entrega(
                id_destinatario=(
                    destinatario.id_destinatario
                ),
                id_requisito_solicitud=(
                    requisito.id_requisito_solicitud
                ),
                estado="en_revision",
                observaciones=(
                    observaciones or None
                ),
                fecha_primera_entrega=ahora,
                fecha_actualizacion=ahora,
            )

            db.session.add(
                entrega
            )

            db.session.flush()

            numero_version = 1

        else:
            ultima = obtener_ultima_version(
                entrega
            )

            numero_version = (
                ultima.numero_version + 1
                if ultima
                else 1
            )

            entrega.estado = (
                "en_revision"
            )

            entrega.observaciones = (
                observaciones or None
            )

            entrega.fecha_actualizacion = (
                ahora
            )

            if not entrega.fecha_primera_entrega:
                entrega.fecha_primera_entrega = (
                    ahora
                )

        # -----------------------------------------
        # GUARDAR ARCHIVO
        # -----------------------------------------

        carpeta = (
            storage_root()
            / str(solicitud.id_ciclo)
            / str(solicitud.id_solicitud)
            / str(destinatario.id_docente)
            / str(entrega.id_entrega)
        )

        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        nombre_guardado = (
            f"v{numero_version}_"
            f"{uuid4().hex}_"
            f"{nombre_original}"
        )

        ruta_absoluta = (
            carpeta
            / nombre_guardado
        )

        ruta_absoluta.write_bytes(
            contenido
        )

        hash_archivo = (
            hashlib.sha256(
                contenido
            ).hexdigest()
        )

        ruta_relativa = (
            ruta_absoluta
            .relative_to(
                backend_root()
            )
            .as_posix()
        )

        try:
            id_usuario = int(
                get_jwt_identity()
            )
        except (TypeError, ValueError):
            raise ValueError(
                "Usuario no válido."
            )

        version = VersionEntrega(
            id_entrega=(
                entrega.id_entrega
            ),
            numero_version=(
                numero_version
            ),
            nombre_archivo=(
                nombre_original
            ),
            ruta_archivo=(
                ruta_relativa
            ),
            tipo_mime=(
                MIME_POR_EXTENSION.get(
                    extension,
                    archivo.mimetype
                    or "application/octet-stream",
                )
            ),
            tamano_bytes=(
                len(contenido)
            ),
            hash_archivo=(
                hash_archivo
            ),
            comentario=(
                observaciones or None
            ),
            id_usuario=(
                id_usuario
            ),
        )

        db.session.add(
            version
        )

        destinatario.estado = (
            "entregado"
        )

        if not destinatario.fecha_lectura:
            destinatario.fecha_lectura = (
                ahora
            )

        db.session.commit()

        return jsonify({
            "mensaje": (
                "Entrega realizada correctamente."
                if numero_version == 1
                else "Corrección enviada correctamente."
            ),

            "entrega": {
                "id_entrega":
                    entrega.id_entrega,

                "estado":
                    entrega.estado,

                "numero_version":
                    numero_version,

                "archivo":
                    nombre_original,
            },
        }), 201

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            "mensaje":
                str(error)
        }), 400

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ENTREGA DOCENTE:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible guardar la entrega."
        }), 500


# =========================================================
# VER ARCHIVO
# =========================================================

@docente_solicitudes_bp.get(
    "/versiones/<int:id_version>/ver"
)
@permission_required("solicitudes.ver")
def ver_archivo(
    id_version,
):
    version = db.session.get(
        VersionEntrega,
        id_version,
    )

    if not version:
        return jsonify({
            "mensaje":
                "El archivo no existe."
        }), 404

    entrega = version.entrega

    if not entrega:
        return jsonify({
            "mensaje":
                "La entrega no existe."
        }), 404

    destinatario = (
        obtener_destinatario_docente(
            entrega.id_destinatario
        )
    )

    if not destinatario:
        return jsonify({
            "mensaje":
                "No tiene permiso para consultar este archivo."
        }), 403

    ruta = (
        backend_root()
        / version.ruta_archivo
    )

    if not ruta.exists():
        return jsonify({
            "mensaje":
                "El archivo físico no fue encontrado."
        }), 404

    return send_file(
        ruta,
        mimetype=version.tipo_mime,
        as_attachment=False,
        download_name=version.nombre_archivo,
    )


# =========================================================
# DESCARGAR ARCHIVO
# =========================================================

@docente_solicitudes_bp.get(
    "/versiones/<int:id_version>/descargar"
)
@permission_required("solicitudes.ver")
def descargar_archivo(
    id_version,
):
    version = db.session.get(
        VersionEntrega,
        id_version,
    )

    if not version:
        return jsonify({
            "mensaje":
                "El archivo no existe."
        }), 404

    entrega = version.entrega

    if not entrega:
        return jsonify({
            "mensaje":
                "La entrega no existe."
        }), 404

    destinatario = (
        obtener_destinatario_docente(
            entrega.id_destinatario
        )
    )

    if not destinatario:
        return jsonify({
            "mensaje":
                "No tiene permiso para descargar este archivo."
        }), 403

    ruta = (
        backend_root()
        / version.ruta_archivo
    )

    if not ruta.exists():
        return jsonify({
            "mensaje":
                "El archivo físico no fue encontrado."
        }), 404

    return send_file(
        ruta,
        mimetype=version.tipo_mime,
        as_attachment=True,
        download_name=version.nombre_archivo,
    )