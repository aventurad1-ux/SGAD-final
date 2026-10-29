from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
)

from app.extensions import db
from app.models import (
    CicloEscolar,
    DocumentoInstitucional,
    VersionDocumentoInstitucional,
)
from app.utils.permissions import permission_required


papelera_bp = Blueprint(
    "papelera",
    __name__,
    url_prefix="/api/directora/papelera",
)


BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)


MIME_PREVIEW = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


# =========================================================
# UTILIDADES
# =========================================================

def nombre_usuario(usuario):
    if not usuario:
        return "Sin registro"

    nombre = (
        f"{usuario.nombres or ''} "
        f"{usuario.apellidos or ''}"
    ).strip()

    return nombre or "Sin registro"


def obtener_ciclo(id_ciclo=None):
    if id_ciclo:
        return db.session.get(
            CicloEscolar,
            id_ciclo,
        )

    ciclo = (
        CicloEscolar.query
        .filter_by(
            estado="activo"
        )
        .order_by(
            CicloEscolar.anio.desc()
        )
        .first()
    )

    if ciclo:
        return ciclo

    return (
        CicloEscolar.query
        .order_by(
            CicloEscolar.anio.desc()
        )
        .first()
    )


def serializar_ciclo(ciclo):
    if not ciclo:
        return None

    return {
        "id_ciclo":
            ciclo.id_ciclo,

        "anio":
            ciclo.anio,

        "estado":
            ciclo.estado,

        "editable":
            ciclo.estado == "activo",
    }


def obtener_ultima_version(documento):
    if not documento:
        return None

    return (
        VersionDocumentoInstitucional.query
        .filter_by(
            id_documento=
                documento.id_documento
        )
        .order_by(
            VersionDocumentoInstitucional
            .numero_version
            .desc()
        )
        .first()
    )


def obtener_versiones(documento):
    if not documento:
        return []

    return (
        VersionDocumentoInstitucional.query
        .filter_by(
            id_documento=
                documento.id_documento
        )
        .order_by(
            VersionDocumentoInstitucional
            .numero_version
            .desc()
        )
        .all()
    )


def ruta_version(version):
    if not version:
        return None

    ruta = Path(
        version.ruta_archivo
    )

    if ruta.is_absolute():
        return ruta

    return (
        BACKEND_DIR
        / ruta
    )


def serializar_version(version):
    if not version:
        return None

    return {
        "id_version":
            version.id_version,

        "numero_version":
            version.numero_version,

        "nombre_archivo":
            version.nombre_archivo,

        "tipo_mime":
            version.tipo_mime,

        "tamano_bytes":
            version.tamano_bytes,

        "motivo":
            version.motivo,

        "responsable":
            nombre_usuario(
                getattr(
                    version,
                    "usuario",
                    None,
                )
            ),

        "fecha_subida": (
            version.fecha_subida.isoformat()
            if version.fecha_subida
            else None
        ),
    }


def serializar_documento(
    documento,
    incluir_versiones=False,
):
    version_actual = (
        obtener_ultima_version(
            documento
        )
    )

    categoria = getattr(
        documento,
        "categoria",
        None,
    )

    ciclo = getattr(
        documento,
        "ciclo",
        None,
    )

    eliminado_por = getattr(
        documento,
        "usuario_papelera",
        None,
    )

    resultado = {
        "tipo":
            "repositorio",

        "origen":
            "Repositorio",

        "id_documento":
            documento.id_documento,

        "codigo":
            documento.codigo,

        "titulo":
            documento.titulo,

        "descripcion":
            documento.descripcion,

        "id_ciclo":
            documento.id_ciclo,

        "ciclo":
            ciclo.anio
            if ciclo
            else None,

        "id_categoria":
            documento.id_categoria,

        "categoria":
            categoria.nombre
            if categoria
            else "Sin categoría",

        "estado":
            documento.estado,

        "nivel_acceso":
            documento.nivel_acceso,

        "version_actual":
            documento.version_actual,

        "en_papelera":
            documento.en_papelera,

        "eliminado_por":
            nombre_usuario(
                eliminado_por
            ),

        "fecha_papelera": (
            documento.fecha_papelera
            .isoformat()
            if documento.fecha_papelera
            else None
        ),

        "archivo": (
            {
                "id_version":
                    version_actual.id_version,

                "numero_version":
                    version_actual.numero_version,

                "nombre_archivo":
                    version_actual.nombre_archivo,

                "tipo_mime":
                    version_actual.tipo_mime,

                "tamano_bytes":
                    version_actual.tamano_bytes,
            }
            if version_actual
            else None
        ),
    }

    if incluir_versiones:
        resultado["versiones"] = [
            serializar_version(
                version
            )
            for version
            in obtener_versiones(
                documento
            )
        ]

    return resultado


def validar_ciclo_editable(ciclo):
    if not ciclo:
        return (
            False,
            "El ciclo escolar no existe.",
        )

    if ciclo.estado != "activo":
        return (
            False,
            (
                "El ciclo seleccionado es histórico "
                "y está disponible únicamente "
                "para consulta."
            ),
        )

    return True, None


# =========================================================
# LISTAR PAPELERA
# =========================================================

@papelera_bp.get("")
@permission_required("documentos.ver")
def listar_papelera():
    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    ciclo = obtener_ciclo(
        id_ciclo
    )

    if not ciclo:
        return jsonify({
            "mensaje":
                "No se encontró el ciclo escolar.",
        }), 404

    documentos = (
        DocumentoInstitucional.query
        .filter_by(
            id_ciclo=
                ciclo.id_ciclo,

            en_papelera=
                True,
        )
        .order_by(
            DocumentoInstitucional
            .fecha_papelera
            .desc()
        )
        .all()
    )

    return jsonify({
        "ciclo":
            serializar_ciclo(
                ciclo
            ),

        "total":
            len(documentos),

        "documentos": [
            serializar_documento(
                documento
            )
            for documento
            in documentos
        ],
    }), 200


# =========================================================
# DETALLE DEL DOCUMENTO
# =========================================================

@papelera_bp.get(
    "/repositorio/<int:id_documento>"
)
@permission_required("documentos.ver")
def detalle_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or not documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no se encuentra en la papelera.",
        }), 404

    return jsonify({
        "documento":
            serializar_documento(
                documento,
                incluir_versiones=True,
            ),
    }), 200


# =========================================================
# RESTAURAR DOCUMENTO
# =========================================================

@papelera_bp.patch(
    "/repositorio/<int:id_documento>/restaurar"
)
@permission_required("documentos.actualizar")
def restaurar_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe.",
        }), 404

    if not documento.en_papelera:
        return jsonify({
            "mensaje":
                "El documento ya se encuentra restaurado.",
        }), 400

    ciclo = obtener_ciclo(
        documento.id_ciclo
    )

    editable, error = (
        validar_ciclo_editable(
            ciclo
        )
    )

    if not editable:
        return jsonify({
            "mensaje":
                error,
        }), 400

    try:
        documento.en_papelera = False

        documento.fecha_papelera = None

        documento.id_usuario_papelera = None

        documento.fecha_actualizacion = (
            datetime.utcnow()
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Documento restaurado correctamente.",

            "documento":
                serializar_documento(
                    documento
                ),
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR RESTAURAR DOCUMENTO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible restaurar el documento.",
        }), 500


# =========================================================
# VER ARCHIVO
# =========================================================

@papelera_bp.get(
    "/repositorio/<int:id_documento>/ver"
)
@permission_required("documentos.ver")
def ver_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or not documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no se encuentra en la papelera.",
        }), 404

    version = obtener_ultima_version(
        documento
    )

    if not version:
        return jsonify({
            "mensaje":
                "El documento no tiene archivo.",
        }), 404

    ruta = ruta_version(
        version
    )

    if (
        not ruta
        or not ruta.exists()
    ):
        return jsonify({
            "mensaje":
                "El archivo físico no está disponible.",
        }), 404

    if (
        version.tipo_mime
        not in MIME_PREVIEW
    ):
        return jsonify({
            "mensaje": (
                "Este formato no admite vista previa. "
                "Utilice Descargar."
            ),
        }), 400

    return send_file(
        ruta,
        mimetype=
            version.tipo_mime,
        as_attachment=False,
        download_name=
            version.nombre_archivo,
    )


# =========================================================
# DESCARGAR ARCHIVO
# =========================================================

@papelera_bp.get(
    "/repositorio/<int:id_documento>/descargar"
)
@permission_required("documentos.descargar")
def descargar_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or not documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no se encuentra en la papelera.",
        }), 404

    version = obtener_ultima_version(
        documento
    )

    if not version:
        return jsonify({
            "mensaje":
                "El documento no tiene archivo.",
        }), 404

    ruta = ruta_version(
        version
    )

    if (
        not ruta
        or not ruta.exists()
    ):
        return jsonify({
            "mensaje":
                "El archivo físico no está disponible.",
        }), 404

    return send_file(
        ruta,
        mimetype=
            version.tipo_mime,
        as_attachment=True,
        download_name=
            version.nombre_archivo,
    )


# =========================================================
# ELIMINAR DEFINITIVAMENTE
# =========================================================

@papelera_bp.delete(
    "/repositorio/<int:id_documento>"
)
@permission_required("documentos.actualizar")
def eliminar_definitivamente(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe.",
        }), 404

    if not documento.en_papelera:
        return jsonify({
            "mensaje": (
                "El documento debe encontrarse en "
                "la papelera antes de eliminarlo "
                "definitivamente."
            ),
        }), 400

    ciclo = obtener_ciclo(
        documento.id_ciclo
    )

    editable, error = (
        validar_ciclo_editable(
            ciclo
        )
    )

    if not editable:
        return jsonify({
            "mensaje":
                error,
        }), 400

    versiones = (
        obtener_versiones(
            documento
        )
    )

    rutas_archivos = []

    for version in versiones:
        ruta = ruta_version(
            version
        )

        if ruta:
            rutas_archivos.append(
                ruta
            )

    try:
        for version in versiones:
            db.session.delete(
                version
            )

        db.session.delete(
            documento
        )

        db.session.commit()

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ELIMINAR DOCUMENTO:",
            repr(error),
        )

        return jsonify({
            "mensaje": (
                "No fue posible eliminar "
                "definitivamente el documento."
            ),
        }), 500

    # -----------------------------------------------------
    # BORRAR ARCHIVOS FÍSICOS
    # -----------------------------------------------------

    for ruta in rutas_archivos:
        try:
            if (
                ruta.exists()
                and ruta.is_file()
            ):
                ruta.unlink()

        except OSError as error:
            print(
                "ADVERTENCIA AL BORRAR ARCHIVO:",
                ruta,
                repr(error),
            )

    return jsonify({
        "mensaje":
            "Documento eliminado definitivamente.",
    }), 200