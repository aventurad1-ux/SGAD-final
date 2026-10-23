from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    jsonify,
    request,
    send_file,
)
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    CicloEscolar,
    DocumentoEstudiante,
    Estudiante,
    Matricula,
    RequisitoExpediente,
    Seccion,
    Usuario,
    VersionDocumentoEstudiante,
)
from app.utils.permissions import permission_required


expedientes_bp = Blueprint(
    "expedientes",
    __name__,
    url_prefix="/api/directora/expedientes",
)


# =========================================================
# CONFIGURACIÓN DE ARCHIVOS
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]

STORAGE_DIR = (
    BACKEND_DIR
    / "storage"
    / "expedientes"
)

STORAGE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MAX_FILE_SIZE = 10 * 1024 * 1024

EXTENSIONES_PERMITIDAS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".jpg",
    ".jpeg",
    ".png",
}

MIME_PREVIEW = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


# =========================================================
# HELPERS
# =========================================================

def nombre_usuario(usuario):
    if not usuario:
        return "Sin asignar"

    return (
        f"{usuario.nombres or ''} "
        f"{usuario.apellidos or ''}"
    ).strip()


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


def obtener_ciclo(id_ciclo):
    return db.session.get(
        CicloEscolar,
        id_ciclo,
    )


def validar_ciclo_editable(ciclo):
    if not ciclo:
        return False, (
            "El ciclo escolar no existe."
        )

    if ciclo.estado != "activo":
        return False, (
            "El ciclo seleccionado es histórico. "
            "Solo está disponible para consulta."
        )

    return True, None


def requisitos_activos():
    return (
        RequisitoExpediente.query
        .filter_by(activo=True)
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


def estado_expediente(
    id_estudiante,
    id_ciclo,
):
    requisitos = [
        req
        for req in requisitos_activos()
        if req.obligatorio
    ]

    documentos = documentos_estudiante(
        id_estudiante,
        id_ciclo,
    )

    entregados_ids = {
        documento.id_requisito
        for documento in documentos
    }

    total = len(requisitos)

    entregados = sum(
        1
        for requisito in requisitos
        if requisito.id_requisito
        in entregados_ids
    )

    return {
        "completo": (
            total > 0
            and entregados == total
        ),
        "entregados": entregados,
        "total": total,
    }


def serializar_seccion(
    seccion,
    id_ciclo,
):
    matriculas = (
        Matricula.query
        .filter_by(
            id_ciclo=id_ciclo,
            id_seccion=
                seccion.id_seccion,
            estado="Activa",
        )
        .all()
    )

    incompletos = 0

    for matricula in matriculas:
        estado = estado_expediente(
            matricula.id_estudiante,
            id_ciclo,
        )

        if not estado["completo"]:
            incompletos += 1

    return {
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

        "docente":
            nombre_usuario(
                seccion.docente
            ),

        "id_docente":
            seccion.id_docente,

        "estudiantes":
            len(matriculas),

        "incompletos":
            incompletos,
    }


def serializar_matricula(
    matricula,
):
    estudiante = matricula.estudiante
    seccion = matricula.seccion

    estado = estado_expediente(
        estudiante.id_estudiante,
        matricula.id_ciclo,
    )

    return {
        "id_matricula":
            matricula.id_matricula,

        "id_estudiante":
            estudiante.id_estudiante,

        "nombre": (
            f"{estudiante.nombres} "
            f"{estudiante.apellidos}"
        ),

        "nombres":
            estudiante.nombres,

        "apellidos":
            estudiante.apellidos,

        "codigo":
            estudiante.codigo,

        "cui":
            estudiante.cui,

        "encargado":
            estudiante.encargado,

        "id_seccion":
            seccion.id_seccion
            if seccion
            else None,

        "seccion":
            etiqueta_seccion(
                seccion
            ),

        "expediente": {
            "completo":
                estado["completo"],

            "entregados":
                estado["entregados"],

            "total":
                estado["total"],
        },
    }


def obtener_ultima_version(
    documento,
):
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


def validar_archivo(archivo):
    if not archivo:
        return (
            False,
            "Debe seleccionar un archivo.",
        )

    nombre = secure_filename(
        archivo.filename or ""
    )

    if not nombre:
        return (
            False,
            "El nombre del archivo no es válido.",
        )

    extension = (
        Path(nombre)
        .suffix
        .lower()
    )

    if (
        extension
        not in EXTENSIONES_PERMITIDAS
    ):
        return (
            False,
            (
                "Formato no permitido. "
                "Use PDF, DOCX, XLSX, "
                "JPG, JPEG o PNG."
            ),
        )

    archivo.stream.seek(
        0,
        2,
    )

    tamano = (
        archivo.stream.tell()
    )

    archivo.stream.seek(0)

    if tamano > MAX_FILE_SIZE:
        return (
            False,
            "El archivo supera los 10 MB.",
        )

    if tamano <= 0:
        return (
            False,
            "El archivo está vacío.",
        )

    return True, {
        "nombre": nombre,
        "extension": extension,
        "tamano": tamano,
    }


def generar_codigo_estudiante(
    anio,
):
    prefijo = f"EORM-{anio}-"

    estudiantes = (
        Estudiante.query
        .filter(
            Estudiante.codigo.like(
                f"{prefijo}%"
            )
        )
        .all()
    )

    mayor = 0

    for estudiante in estudiantes:
        try:
            numero = int(
                estudiante.codigo
                .split("-")[-1]
            )

            mayor = max(
                mayor,
                numero,
            )
        except (
            ValueError,
            AttributeError,
        ):
            continue

    return (
        f"{prefijo}"
        f"{mayor + 1:03d}"
    )


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================

@expedientes_bp.get("")
@permission_required("estudiantes.ver")
def listar_expedientes():
    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    if not id_ciclo:
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

        if not ciclo:
            return jsonify({
                "mensaje":
                    "No existe un ciclo escolar activo."
            }), 404

        id_ciclo = ciclo.id_ciclo

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
            id_ciclo=id_ciclo,
            activo=True,
        )
        .order_by(
            Seccion.grado.asc(),
            Seccion.nombre.asc(),
        )
        .all()
    )

    matriculas = (
        Matricula.query
        .filter_by(
            id_ciclo=id_ciclo,
            estado="Activa",
        )
        .order_by(
            Matricula.id_matricula.asc()
        )
        .all()
    )

    return jsonify({
        "ciclo": {
            "id_ciclo":
                ciclo.id_ciclo,

            "anio":
                ciclo.anio,

            "estado":
                ciclo.estado,

            "editable":
                ciclo.estado
                == "activo",
        },

        "secciones": [
            serializar_seccion(
                seccion,
                id_ciclo,
            )
            for seccion
            in secciones
        ],

        "estudiantes": [
            serializar_matricula(
                matricula
            )
            for matricula
            in matriculas
        ],
    }), 200


# =========================================================
# CATÁLOGOS PARA MATRÍCULA
# =========================================================

@expedientes_bp.get("/catalogos")
@permission_required("estudiantes.ver")
def catalogos_expedientes():
    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    if not id_ciclo:
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

        if not ciclo:
            return jsonify({
                "mensaje":
                    "No existe ciclo activo."
            }), 404

        id_ciclo = ciclo.id_ciclo

    secciones = (
        Seccion.query
        .filter_by(
            id_ciclo=id_ciclo,
            activo=True,
        )
        .order_by(
            Seccion.grado.asc()
        )
        .all()
    )

    matriculados_ids = {
        matricula.id_estudiante
        for matricula
        in Matricula.query
        .filter_by(
            id_ciclo=id_ciclo
        )
        .all()
    }

    disponibles = (
        Estudiante.query
        .filter_by(
            activo=True
        )
        .order_by(
            Estudiante.apellidos.asc(),
            Estudiante.nombres.asc(),
        )
        .all()
    )

    disponibles = [
        estudiante
        for estudiante
        in disponibles
        if estudiante.id_estudiante
        not in matriculados_ids
    ]

    return jsonify({
        "secciones": [
            {
                "id_seccion":
                    seccion.id_seccion,

                "etiqueta":
                    etiqueta_seccion(
                        seccion
                    ),

                "docente":
                    nombre_usuario(
                        seccion.docente
                    ),
            }
            for seccion
            in secciones
        ],

        "estudiantes_disponibles": [
            {
                "id_estudiante":
                    estudiante.id_estudiante,

                "nombre": (
                    f"{estudiante.nombres} "
                    f"{estudiante.apellidos}"
                ),

                "cui":
                    estudiante.cui,

                "codigo":
                    estudiante.codigo,
            }
            for estudiante
            in disponibles
        ],
    }), 200


# =========================================================
# NUEVA MATRÍCULA / REINSCRIPCIÓN
# =========================================================

@expedientes_bp.post("/matriculas")
@permission_required("estudiantes.ver")
def crear_matricula():
    data = request.get_json() or {}

    modo = data.get(
        "modo",
        "new",
    )

    id_ciclo = data.get(
        "id_ciclo"
    )

    id_seccion = data.get(
        "id_seccion"
    )

    if not id_ciclo:
        return jsonify({
            "mensaje":
                "Debe indicar el ciclo."
        }), 400

    if not id_seccion:
        return jsonify({
            "mensaje":
                "Seleccione grado y sección."
        }), 400

    ciclo = obtener_ciclo(
        int(id_ciclo)
    )

    editable, error = (
        validar_ciclo_editable(
            ciclo
        )
    )

    if not editable:
        return jsonify({
            "mensaje": error
        }), 400

    seccion = db.session.get(
        Seccion,
        int(id_seccion),
    )

    if (
        not seccion
        or seccion.id_ciclo
        != ciclo.id_ciclo
        or not seccion.activo
    ):
        return jsonify({
            "mensaje":
                "La sección seleccionada no es válida."
        }), 400

    try:
        if modo == "existing":
            id_estudiante = data.get(
                "id_estudiante"
            )

            estudiante = db.session.get(
                Estudiante,
                int(id_estudiante)
                if id_estudiante
                else 0,
            )

            if not estudiante:
                raise ValueError(
                    "El estudiante no existe."
                )

        else:
            nombres = str(
                data.get(
                    "nombres",
                    ""
                )
            ).strip()

            apellidos = str(
                data.get(
                    "apellidos",
                    ""
                )
            ).strip()

            cui = str(
                data.get(
                    "cui",
                    ""
                )
            ).strip()

            nacimiento = data.get(
                "fecha_nacimiento"
            )

            genero = str(
                data.get(
                    "genero",
                    ""
                )
            ).strip()

            direccion = str(
                data.get(
                    "direccion",
                    ""
                )
            ).strip()

            encargado = str(
                data.get(
                    "encargado",
                    ""
                )
            ).strip()

            parentesco = str(
                data.get(
                    "parentesco",
                    ""
                )
            ).strip()

            telefono = str(
                data.get(
                    "telefono",
                    ""
                )
            ).strip()

            if not all([
                nombres,
                apellidos,
                cui,
                nacimiento,
                genero,
                direccion,
                encargado,
                parentesco,
                telefono,
            ]):
                raise ValueError(
                    "Complete todos los campos obligatorios."
                )

            if (
                len(cui) != 13
                or not cui.isdigit()
            ):
                raise ValueError(
                    "El CUI debe contener 13 dígitos."
                )

            if (
                len(telefono) != 8
                or not telefono.isdigit()
            ):
                raise ValueError(
                    "El teléfono debe contener 8 dígitos."
                )

            if Estudiante.query.filter_by(
                cui=cui
            ).first():
                raise ValueError(
                    "Ya existe un estudiante registrado con ese CUI."
                )

            try:
                fecha_nacimiento = (
                    date.fromisoformat(
                        nacimiento
                    )
                )
            except ValueError:
                raise ValueError(
                    "La fecha de nacimiento no es válida."
                )

            edad = (
                ciclo.anio
                - fecha_nacimiento.year
            )

            if edad < 4 or edad > 16:
                raise ValueError(
                    "La edad indicada está fuera del rango escolar esperado."
                )

            estudiante = Estudiante(
                codigo=
                    generar_codigo_estudiante(
                        ciclo.anio
                    ),

                cui=cui,
                nombres=nombres,
                apellidos=apellidos,

                fecha_nacimiento=
                    fecha_nacimiento,

                genero=genero,
                direccion=direccion,
                encargado=encargado,
                parentesco=parentesco,
                telefono=telefono,
                activo=True,
            )

            db.session.add(
                estudiante
            )

            db.session.flush()

        existente = (
            Matricula.query
            .filter_by(
                id_estudiante=
                    estudiante.id_estudiante,

                id_ciclo=
                    ciclo.id_ciclo,
            )
            .first()
        )

        if existente:
            raise ValueError(
                "El estudiante ya está matriculado en este ciclo."
            )

        matricula = Matricula(
            id_estudiante=
                estudiante.id_estudiante,

            id_ciclo=
                ciclo.id_ciclo,

            id_seccion=
                seccion.id_seccion,

            estado="Activa",
        )

        db.session.add(
            matricula
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Matrícula guardada correctamente.",

            "matricula":
                serializar_matricula(
                    matricula
                ),
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
            "ERROR MATRÍCULA:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible guardar la matrícula."
        }), 500


# =========================================================
# DETALLE DEL EXPEDIENTE
# =========================================================

@expedientes_bp.get(
    "/estudiantes/<int:id_estudiante>"
)
@permission_required("estudiantes.ver")
def detalle_expediente(
    id_estudiante
):
    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    if not id_ciclo:
        return jsonify({
            "mensaje":
                "Debe indicar el ciclo."
        }), 400

    estudiante = db.session.get(
        Estudiante,
        id_estudiante,
    )

    if not estudiante:
        return jsonify({
            "mensaje":
                "El estudiante no existe."
        }), 404

    matricula = (
        Matricula.query
        .filter_by(
            id_estudiante=
                id_estudiante,

            id_ciclo=
                id_ciclo,
        )
        .first()
    )

    if not matricula:
        return jsonify({
            "mensaje":
                "No existe matrícula del estudiante en este ciclo."
        }), 404

    ciclo = obtener_ciclo(
        id_ciclo
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

            "id_documento":
                documento.id_documento
                if documento
                else None,

            "version":
                documento.version_actual
                if documento
                else None,

            "archivo":
                ultima_version.nombre_archivo
                if ultima_version
                else None,

            "tipo_mime":
                ultima_version.tipo_mime
                if ultima_version
                else None,

            "observaciones":
                documento.observaciones
                if documento
                else None,
        })

    estado = estado_expediente(
        id_estudiante,
        id_ciclo,
    )

    return jsonify({
        "estudiante": {
            "id_estudiante":
                estudiante.id_estudiante,

            "nombre": (
                f"{estudiante.nombres} "
                f"{estudiante.apellidos}"
            ),

            "codigo":
                estudiante.codigo,

            "cui":
                estudiante.cui,

            "encargado":
                estudiante.encargado,

            "parentesco":
                estudiante.parentesco,

            "telefono":
                estudiante.telefono,

            "direccion":
                estudiante.direccion,

            "fecha_nacimiento":
                estudiante.fecha_nacimiento.isoformat(),

            "genero":
                estudiante.genero,
        },

        "matricula": {
            "id_matricula":
                matricula.id_matricula,

            "ciclo":
                ciclo.anio,

            "id_ciclo":
                ciclo.id_ciclo,

            "seccion":
                etiqueta_seccion(
                    matricula.seccion
                ),

            "docente":
                nombre_usuario(
                    matricula.seccion.docente
                    if matricula.seccion
                    else None
                ),

            "editable":
                ciclo.estado
                == "activo",
        },

        "estado": estado,

        "requisitos":
            requisitos,
    }), 200


# =========================================================
# SUBIR / ACTUALIZAR DOCUMENTO
# =========================================================

@expedientes_bp.post(
    "/estudiantes/<int:id_estudiante>/documentos"
)
@permission_required("documentos.ver")
def guardar_documento(
    id_estudiante
):
    id_ciclo = request.form.get(
        "id_ciclo",
        type=int,
    )

    id_requisito = request.form.get(
        "id_requisito",
        type=int,
    )

    observaciones = str(
        request.form.get(
            "observaciones",
            ""
        )
    ).strip()

    archivo = request.files.get(
        "archivo"
    )

    if not id_ciclo:
        return jsonify({
            "mensaje":
                "Debe indicar el ciclo."
        }), 400

    if not id_requisito:
        return jsonify({
            "mensaje":
                "Debe seleccionar el documento."
        }), 400

    ciclo = obtener_ciclo(
        id_ciclo
    )

    editable, error = (
        validar_ciclo_editable(
            ciclo
        )
    )

    if not editable:
        return jsonify({
            "mensaje": error
        }), 400

    estudiante = db.session.get(
        Estudiante,
        id_estudiante,
    )

    if not estudiante:
        return jsonify({
            "mensaje":
                "El estudiante no existe."
        }), 404

    matricula = (
        Matricula.query
        .filter_by(
            id_estudiante=id_estudiante,
            id_ciclo=id_ciclo,
        )
        .first()
    )

    if not matricula:
        return jsonify({
            "mensaje":
                "El estudiante no está matriculado en este ciclo."
        }), 400

    requisito = db.session.get(
        RequisitoExpediente,
        id_requisito,
    )

    if (
        not requisito
        or not requisito.activo
    ):
        return jsonify({
            "mensaje":
                "El requisito seleccionado no es válido."
        }), 400

    valido, datos_archivo = (
        validar_archivo(
            archivo
        )
    )

    if not valido:
        return jsonify({
            "mensaje":
                datos_archivo
        }), 400

    contenido = archivo.read()

    hash_archivo = sha256(
        contenido
    ).hexdigest()

    extension = (
        datos_archivo["extension"]
    )

    carpeta = (
        STORAGE_DIR
        / str(id_ciclo)
        / str(id_estudiante)
    )

    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )

    nombre_interno = (
        f"{uuid4().hex}"
        f"{extension}"
    )

    ruta_absoluta = (
        carpeta
        / nombre_interno
    )

    ruta_relativa = (
        ruta_absoluta
        .relative_to(
            BACKEND_DIR
        )
    )

    ruta_absoluta.write_bytes(
        contenido
    )

    try:
        id_usuario = int(
            get_jwt_identity()
        )

        documento = (
            DocumentoEstudiante.query
            .filter_by(
                id_estudiante=
                    id_estudiante,

                id_ciclo=
                    id_ciclo,

                id_requisito=
                    id_requisito,
            )
            .first()
        )

        if documento:
            nueva_version = (
                documento.version_actual
                + 1
            )

            documento.version_actual = (
                nueva_version
            )

            documento.estado = (
                "Entregado"
            )

            documento.observaciones = (
                observaciones
            )

            documento.id_usuario = (
                id_usuario
            )

        else:
            nueva_version = 1

            documento = (
                DocumentoEstudiante(
                    id_estudiante=
                        id_estudiante,

                    id_ciclo=
                        id_ciclo,

                    id_requisito=
                        id_requisito,

                    version_actual=1,

                    estado=
                        "Entregado",

                    observaciones=
                        observaciones,

                    id_usuario=
                        id_usuario,
                )
            )

            db.session.add(
                documento
            )

            db.session.flush()

        version = (
            VersionDocumentoEstudiante(
                id_documento=
                    documento.id_documento,

                numero_version=
                    nueva_version,

                nombre_archivo=
                    datos_archivo["nombre"],

                ruta_archivo=
                    str(
                        ruta_relativa
                    ),

                tipo_mime=(
                    archivo.mimetype
                    or "application/octet-stream"
                ),

                tamano_bytes=
                    datos_archivo["tamano"],

                hash_archivo=
                    hash_archivo,

                motivo=(
                    observaciones
                    or (
                        "Carga inicial"
                        if nueva_version == 1
                        else "Actualización"
                    )
                ),

                id_usuario=
                    id_usuario,
            )
        )

        db.session.add(
            version
        )

        db.session.commit()

        return jsonify({
            "mensaje": (
                "Documento actualizado correctamente."
                if nueva_version > 1
                else "Documento guardado correctamente."
            ),

            "id_documento":
                documento.id_documento,

            "version":
                nueva_version,
        }), 201

    except Exception as error:
        db.session.rollback()

        if ruta_absoluta.exists():
            ruta_absoluta.unlink()

        print(
            "ERROR DOCUMENTO EXPEDIENTE:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible guardar el documento."
        }), 500


# =========================================================
# VER ARCHIVO
# =========================================================

@expedientes_bp.get(
    "/documentos/<int:id_documento>/ver"
)
@permission_required("documentos.ver")
def ver_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoEstudiante,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

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
            "mensaje":
                "El archivo físico no está disponible."
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
# DESCARGAR ARCHIVO
# =========================================================

@expedientes_bp.get(
    "/documentos/<int:id_documento>/descargar"
)
@permission_required("documentos.ver")
def descargar_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoEstudiante,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

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
            "mensaje":
                "El archivo físico no está disponible."
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

@expedientes_bp.get(
    "/documentos/<int:id_documento>/versiones"
)
@permission_required("documentos.ver")
def versiones_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoEstudiante,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

    versiones = (
        VersionDocumentoEstudiante.query
        .filter_by(
            id_documento=id_documento
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

                "fecha_subida":
                    version.fecha_subida.isoformat()
                    if version.fecha_subida
                    else None,
            }
            for version
            in versiones
        ]
    }), 200