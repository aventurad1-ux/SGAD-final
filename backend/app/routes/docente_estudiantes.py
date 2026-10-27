from pathlib import Path

from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
)
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import (
    CicloEscolar,
    DocumentoEstudiante,
    Estudiante,
    Matricula,
    RequisitoExpediente,
    Seccion,
    VersionDocumentoEstudiante,
)
from app.utils.permissions import permission_required


docente_estudiantes_bp = Blueprint(
    "docente_estudiantes",
    __name__,
    url_prefix="/api/docente/estudiantes",
)


BACKEND_DIR = Path(__file__).resolve().parents[2]

MIME_PREVIEW = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


# =========================================================
# HELPERS
# =========================================================

def obtener_id_docente():
    return int(
        get_jwt_identity()
    )


def etiqueta_grado(grado):
    nombres = {
        1: "Primero",
        2: "Segundo",
        3: "Tercero",
        4: "Cuarto",
        5: "Quinto",
        6: "Sexto",
    }

    return nombres.get(
        grado,
        f"{grado}°",
    )


def etiqueta_seccion(seccion):
    if not seccion:
        return "Sin sección"

    return (
        f"{etiqueta_grado(seccion.grado)} "
        f"{seccion.nombre}"
    )


def obtener_ciclo(id_ciclo=None):
    if id_ciclo:
        return db.session.get(
            CicloEscolar,
            id_ciclo,
        )

    return (
        CicloEscolar.query
        .filter_by(
            estado="activo"
        )
        .order_by(
            CicloEscolar.anio.desc()
        )
        .first()
    )


def requisitos_activos():
    return (
        RequisitoExpediente.query
        .filter_by(
            activo=True
        )
        .order_by(
            RequisitoExpediente.orden.asc(),
            RequisitoExpediente.id_requisito.asc(),
        )
        .all()
    )


def documentos_estudiante(
    id_estudiante,
    id_ciclo,
):
    return (
        DocumentoEstudiante.query
        .filter_by(
            id_estudiante=id_estudiante,
            id_ciclo=id_ciclo,
        )
        .all()
    )


def obtener_ultima_version(
    documento,
):
    if not documento:
        return None

    return (
        VersionDocumentoEstudiante.query
        .filter_by(
            id_documento=
                documento.id_documento
        )
        .order_by(
            VersionDocumentoEstudiante
            .numero_version
            .desc()
        )
        .first()
    )


def ruta_version(version):
    if not version:
        return None

    ruta = Path(
        version.ruta_archivo
    )

    if ruta.is_absolute():
        return ruta

    return BACKEND_DIR / ruta


def obtener_matricula_permitida(
    id_estudiante,
    id_ciclo,
    id_docente,
):
    """
    Verifica que el estudiante esté matriculado
    en una sección asignada al docente autenticado.
    """

    return (
        Matricula.query
        .join(
            Seccion,
            Matricula.id_seccion
            == Seccion.id_seccion,
        )
        .filter(
            Matricula.id_estudiante
            == id_estudiante,

            Matricula.id_ciclo
            == id_ciclo,

            Matricula.estado
            == "Activa",

            Seccion.id_docente
            == id_docente,

            Seccion.id_ciclo
            == id_ciclo,

            Seccion.activo.is_(True),
        )
        .first()
    )


def estado_expediente(
    id_estudiante,
    id_ciclo,
):
    requisitos = [
        requisito
        for requisito
        in requisitos_activos()
        if requisito.obligatorio
    ]

    documentos = (
        documentos_estudiante(
            id_estudiante,
            id_ciclo,
        )
    )

    requisitos_entregados = {
        documento.id_requisito
        for documento in documentos
    }

    total = len(
        requisitos
    )

    entregados = sum(
        1
        for requisito in requisitos
        if requisito.id_requisito
        in requisitos_entregados
    )

    return {
        "completo": (
            total > 0
            and entregados == total
        ),
        "entregados":
            entregados,
        "total":
            total,
    }


# =========================================================
# LISTADO DE MIS ESTUDIANTES
# =========================================================

@docente_estudiantes_bp.get("")
@permission_required(
    "estudiantes.ver"
)
def listar_mis_estudiantes():
    id_docente = (
        obtener_id_docente()
    )

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
                "El ciclo escolar no existe."
        }), 404

    secciones = (
        Seccion.query
        .filter_by(
            id_ciclo=
                ciclo.id_ciclo,

            id_docente=
                id_docente,

            activo=True,
        )
        .order_by(
            Seccion.grado.asc(),
            Seccion.nombre.asc(),
        )
        .all()
    )

    ids_secciones = [
        seccion.id_seccion
        for seccion
        in secciones
    ]

    matriculas = []

    if ids_secciones:
        matriculas = (
            Matricula.query
            .filter(
                Matricula.id_ciclo
                == ciclo.id_ciclo,

                Matricula.id_seccion
                .in_(
                    ids_secciones
                ),

                Matricula.estado
                == "Activa",
            )
            .order_by(
                Matricula.id_seccion.asc(),
                Matricula.id_matricula.asc(),
            )
            .all()
        )

    estudiantes = []

    for matricula in matriculas:
        estudiante = (
            matricula.estudiante
        )

        estado = (
            estado_expediente(
                estudiante.id_estudiante,
                ciclo.id_ciclo,
            )
        )

        estudiantes.append({
            "id_matricula":
                matricula.id_matricula,

            "id_estudiante":
                estudiante.id_estudiante,

            "codigo":
                estudiante.codigo,

            "nombre": (
                f"{estudiante.nombres} "
                f"{estudiante.apellidos}"
            ),

            "nombres":
                estudiante.nombres,

            "apellidos":
                estudiante.apellidos,

            "cui":
                estudiante.cui,

            "encargado":
                estudiante.encargado,

            "telefono":
                estudiante.telefono,

            "id_seccion":
                matricula.id_seccion,

            "seccion":
                etiqueta_seccion(
                    matricula.seccion
                ),

            "expediente":
                estado,
        })

    secciones_serializadas = []

    for seccion in secciones:
        cantidad = sum(
            1
            for matricula
            in matriculas
            if matricula.id_seccion
            == seccion.id_seccion
        )

        secciones_serializadas.append({
            "id_seccion":
                seccion.id_seccion,

            "grado":
                seccion.grado,

            "nombre":
                seccion.nombre,

            "etiqueta":
                etiqueta_seccion(
                    seccion
                ),

            "estudiantes":
                cantidad,
        })

    return jsonify({
        "ciclo": {
            "id_ciclo":
                ciclo.id_ciclo,

            "anio":
                ciclo.anio,

            "estado":
                ciclo.estado,
        },

        "secciones":
            secciones_serializadas,

        "estudiantes":
            estudiantes,
    }), 200


# =========================================================
# DETALLE DEL EXPEDIENTE
# =========================================================

@docente_estudiantes_bp.get(
    "/<int:id_estudiante>"
)
@permission_required(
    "estudiantes.ver"
)
def detalle_mi_estudiante(
    id_estudiante
):
    id_docente = (
        obtener_id_docente()
    )

    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    if not id_ciclo:
        return jsonify({
            "mensaje":
                "Debe indicar el ciclo escolar."
        }), 400

    ciclo = db.session.get(
        CicloEscolar,
        id_ciclo,
    )

    if not ciclo:
        return jsonify({
            "mensaje":
                "El ciclo escolar no existe."
        }), 404

    matricula = (
        obtener_matricula_permitida(
            id_estudiante,
            id_ciclo,
            id_docente,
        )
    )

    if not matricula:
        return jsonify({
            "mensaje": (
                "No tiene acceso a este estudiante "
                "en el ciclo seleccionado."
            )
        }), 403

    estudiante = (
        matricula.estudiante
    )

    documentos = {
        documento.id_requisito:
            documento
        for documento
        in documentos_estudiante(
            id_estudiante,
            id_ciclo,
        )
    }

    requisitos = []

    for requisito in requisitos_activos():
        documento = documentos.get(
            requisito.id_requisito
        )

        ultima_version = (
            obtener_ultima_version(
                documento
            )
            if documento
            else None
        )

        requisitos.append({
            "id_requisito":
                requisito.id_requisito,

            "nombre":
                requisito.nombre,

            "obligatorio":
                requisito.obligatorio,

            "entregado":
                bool(documento),

            "id_documento": (
                documento.id_documento
                if documento
                else None
            ),

            "version": (
                documento.version_actual
                if documento
                else None
            ),

            "estado": (
                documento.estado
                if documento
                else None
            ),

            "archivo": (
                ultima_version.nombre_archivo
                if ultima_version
                else None
            ),

            "tipo_mime": (
                ultima_version.tipo_mime
                if ultima_version
                else None
            ),

            "observaciones": (
                documento.observaciones
                if documento
                else None
            ),
        })

    return jsonify({
        "estudiante": {
            "id_estudiante":
                estudiante.id_estudiante,

            "codigo":
                estudiante.codigo,

            "nombre": (
                f"{estudiante.nombres} "
                f"{estudiante.apellidos}"
            ),

            "nombres":
                estudiante.nombres,

            "apellidos":
                estudiante.apellidos,

            "cui":
                estudiante.cui,

            "fecha_nacimiento":
                estudiante.fecha_nacimiento.isoformat(),

            "genero":
                estudiante.genero,

            "direccion":
                estudiante.direccion,

            "encargado":
                estudiante.encargado,

            "parentesco":
                estudiante.parentesco,

            "telefono":
                estudiante.telefono,
        },

        "matricula": {
            "id_matricula":
                matricula.id_matricula,

            "id_ciclo":
                ciclo.id_ciclo,

            "ciclo":
                ciclo.anio,

            "id_seccion":
                matricula.id_seccion,

            "seccion":
                etiqueta_seccion(
                    matricula.seccion
                ),
        },

        "estado":
            estado_expediente(
                id_estudiante,
                id_ciclo,
            ),

        "requisitos":
            requisitos,
    }), 200


# =========================================================
# VER DOCUMENTO
# =========================================================

@docente_estudiantes_bp.get(
    "/documentos/<int:id_documento>/ver"
)
@permission_required(
    "documentos.ver"
)
def ver_documento_estudiante(
    id_documento
):
    id_docente = (
        obtener_id_docente()
    )

    documento = db.session.get(
        DocumentoEstudiante,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

    matricula = (
        obtener_matricula_permitida(
            documento.id_estudiante,
            documento.id_ciclo,
            id_docente,
        )
    )

    if not matricula:
        return jsonify({
            "mensaje":
                "No tiene acceso a este documento."
        }), 403

    version = obtener_ultima_version(
        documento
    )

    if not version:
        return jsonify({
            "mensaje":
                "El documento no tiene archivo."
        }), 404

    ruta = ruta_version(
        version
    )

    if (
        not ruta
        or not ruta.exists()
    ):
        return jsonify({
            "mensaje": (
                "El archivo físico "
                "no está disponible."
            )
        }), 404

    if (
        version.tipo_mime
        not in MIME_PREVIEW
    ):
        return jsonify({
            "mensaje": (
                "Este formato no admite vista previa. "
                "Utilice Descargar."
            )
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
# DESCARGAR DOCUMENTO
# =========================================================

@docente_estudiantes_bp.get(
    "/documentos/<int:id_documento>/descargar"
)
@permission_required(
    "documentos.descargar"
)
def descargar_documento_estudiante(
    id_documento
):
    id_docente = (
        obtener_id_docente()
    )

    documento = db.session.get(
        DocumentoEstudiante,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

    matricula = (
        obtener_matricula_permitida(
            documento.id_estudiante,
            documento.id_ciclo,
            id_docente,
        )
    )

    if not matricula:
        return jsonify({
            "mensaje":
                "No tiene acceso a este documento."
        }), 403

    version = obtener_ultima_version(
        documento
    )

    if not version:
        return jsonify({
            "mensaje":
                "El documento no tiene archivo."
        }), 404

    ruta = ruta_version(
        version
    )

    if (
        not ruta
        or not ruta.exists()
    ):
        return jsonify({
            "mensaje": (
                "El archivo físico "
                "no está disponible."
            )
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
# HISTORIAL DE VERSIONES
# =========================================================

@docente_estudiantes_bp.get(
    "/documentos/<int:id_documento>/versiones"
)
@permission_required(
    "documentos.ver"
)
def versiones_documento_estudiante(
    id_documento
):
    id_docente = (
        obtener_id_docente()
    )

    documento = db.session.get(
        DocumentoEstudiante,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

    matricula = (
        obtener_matricula_permitida(
            documento.id_estudiante,
            documento.id_ciclo,
            id_docente,
        )
    )

    if not matricula:
        return jsonify({
            "mensaje":
                "No tiene acceso a este documento."
        }), 403

    versiones = (
        VersionDocumentoEstudiante.query
        .filter_by(
            id_documento=
                id_documento
        )
        .order_by(
            VersionDocumentoEstudiante
            .numero_version
            .desc()
        )
        .all()
    )

    return jsonify({
        "versiones": [
            {
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

                "fecha_subida": (
                    version.fecha_subida.isoformat()
                    if version.fecha_subida
                    else None
                ),
            }
            for version in versiones
        ]
    }), 200