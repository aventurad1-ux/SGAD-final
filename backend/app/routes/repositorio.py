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
    CategoriaRepositorio,
    CicloEscolar,
    DocumentoInstitucional,
    Usuario,
    VersionDocumentoInstitucional,
)

from app.services.bitacora_service import registrar_actividad
from app.utils.permissions import permission_required


repositorio_bp = Blueprint(
    "repositorio",
    __name__,
    url_prefix="/api/directora/repositorio",
)


# =========================================================
# CONFIGURACIÓN DE ARCHIVOS
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]

STORAGE_DIR = (
    BACKEND_DIR
    / "storage"
    / "repositorio"
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


def validar_ciclo_editable(ciclo):
    if not ciclo:
        return (
            False,
            "El ciclo escolar no existe."
        )

    if ciclo.estado != "activo":
        return (
            False,
            (
                "El ciclo seleccionado es histórico. "
                "Solo está disponible para consulta."
            )
        )

    return True, None


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

    tamano = archivo.stream.tell()

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


def generar_codigo_documento(anio):
    prefijo = f"DOC-{anio}-"

    documentos = (
        DocumentoInstitucional.query
        .filter(
            DocumentoInstitucional.codigo.like(
                f"{prefijo}%"
            )
        )
        .all()
    )

    mayor = 0

    for documento in documentos:
        try:
            numero = int(
                documento.codigo
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


def serializar_categoria(categoria):
    return {
        "id_categoria":
            categoria.id_categoria,

        "nombre":
            categoria.nombre,

        "activa":
            categoria.activa,
    }


def serializar_version(version):
    usuario = (
        db.session.get(
            Usuario,
            version.id_usuario,
        )
        if version.id_usuario
        else None
    )

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
                usuario
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
    ultima_version = (
        obtener_ultima_version(
            documento
        )
    )

    resultado = {
        "id_documento":
            documento.id_documento,

        "codigo":
            documento.codigo,

        "id_ciclo":
            documento.id_ciclo,

        "ciclo": (
            documento.ciclo.anio
            if documento.ciclo
            else None
        ),

        "id_categoria":
            documento.id_categoria,

        "categoria": (
            documento.categoria.nombre
            if documento.categoria
            else "Sin categoría"
        ),

        "titulo":
            documento.titulo,

        "descripcion":
            documento.descripcion,

        "fecha_documental": (
            documento.fecha_documental.isoformat()
            if documento.fecha_documental
            else None
        ),

        "nivel_acceso":
            documento.nivel_acceso,

        "nivel_acceso_texto": (
            "Solo Dirección"
            if documento.nivel_acceso
            == "direccion"
            else "Dirección y docentes"
        ),

        "estado":
            documento.estado,

        "version_actual":
            documento.version_actual,

        "responsable":
            nombre_usuario(
                documento.responsable
            ),

        "id_usuario_responsable":
            documento.id_usuario_responsable,

        "en_papelera":
            documento.en_papelera,

        "fecha_papelera": (
            documento.fecha_papelera.isoformat()
            if documento.fecha_papelera
            else None
        ),

        "fecha_creacion": (
            documento.fecha_creacion.isoformat()
            if documento.fecha_creacion
            else None
        ),

        "fecha_actualizacion": (
            documento.fecha_actualizacion.isoformat()
            if documento.fecha_actualizacion
            else None
        ),

        "archivo": (
            {
                "id_version":
                    ultima_version.id_version,

                "nombre_archivo":
                    ultima_version.nombre_archivo,

                "tipo_mime":
                    ultima_version.tipo_mime,

                "tamano_bytes":
                    ultima_version.tamano_bytes,
            }
            if ultima_version
            else None
        ),
    }

    if incluir_versiones:
        versiones = (
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

        resultado["versiones"] = [
            serializar_version(
                version
            )
            for version in versiones
        ]

    return resultado


# =========================================================
# CATEGORÍAS
# =========================================================

@repositorio_bp.get("/categorias")
@permission_required("documentos.ver")
def listar_categorias():
    categorias = (
        CategoriaRepositorio.query
        .order_by(
            CategoriaRepositorio.nombre.asc()
        )
        .all()
    )

    return jsonify({
        "categorias": [
            serializar_categoria(
                categoria
            )
            for categoria in categorias
        ]
    }), 200


@repositorio_bp.post("/categorias")
@permission_required("documentos.actualizar")
def crear_categoria():
    data = request.get_json(
        silent=True
    ) or {}

    nombre = str(
        data.get(
            "nombre",
            ""
        )
    ).strip()

    if not nombre:
        return jsonify({
            "mensaje":
                "Escriba el nombre de la categoría."
        }), 400

    existente = (
        CategoriaRepositorio.query
        .filter(
            db.func.lower(
                CategoriaRepositorio.nombre
            ) == nombre.lower()
        )
        .first()
    )

    if existente:
        return jsonify({
            "mensaje":
                "Ya existe una categoría con ese nombre."
        }), 400

    try:
        categoria = CategoriaRepositorio(
            nombre=nombre,
            activa=True,
        )

        db.session.add(
            categoria
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Categoría creada correctamente.",

            "categoria":
                serializar_categoria(
                    categoria
                ),
        }), 201

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CREAR CATEGORÍA:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible crear la categoría."
        }), 500


@repositorio_bp.patch(
    "/categorias/<int:id_categoria>/estado"
)
@permission_required("documentos.actualizar")
def cambiar_estado_categoria(
    id_categoria
):
    categoria = db.session.get(
        CategoriaRepositorio,
        id_categoria,
    )

    if not categoria:
        return jsonify({
            "mensaje":
                "La categoría no existe."
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    if "activa" not in data:
        return jsonify({
            "mensaje":
                "Indique el estado de la categoría."
        }), 400

    try:
        categoria.activa = bool(
            data.get(
                "activa"
            )
        )

        db.session.commit()

        return jsonify({
            "mensaje": (
                "Categoría activada correctamente."
                if categoria.activa
                else
                "Categoría desactivada correctamente."
            ),

            "categoria":
                serializar_categoria(
                    categoria
                ),
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ESTADO CATEGORÍA:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible cambiar el estado."
        }), 500


# =========================================================
# LISTAR DOCUMENTOS
# =========================================================

@repositorio_bp.get("")
@permission_required("documentos.ver")
def listar_documentos():
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
                "No existe un ciclo escolar disponible."
        }), 404

    consulta = (
        DocumentoInstitucional.query
        .filter_by(
            id_ciclo=ciclo.id_ciclo,
            en_papelera=False,
        )
    )

    texto = str(
        request.args.get(
            "buscar",
            ""
        )
    ).strip()

    id_categoria = request.args.get(
        "id_categoria",
        type=int,
    )

    estado = str(
        request.args.get(
            "estado",
            ""
        )
    ).strip()

    nivel_acceso = str(
        request.args.get(
            "nivel_acceso",
            ""
        )
    ).strip()

    if texto:
        patron = f"%{texto}%"

        consulta = consulta.filter(
            db.or_(
                DocumentoInstitucional.codigo.ilike(
                    patron
                ),

                DocumentoInstitucional.titulo.ilike(
                    patron
                ),

                DocumentoInstitucional.responsable.has(
                    db.or_(
                        Usuario.nombres.ilike(
                            patron
                        ),

                        Usuario.apellidos.ilike(
                            patron
                        ),

                        db.func.concat(
                            Usuario.nombres,
                            " ",
                            Usuario.apellidos
                        ).ilike(
                            patron
                        ),
                    )
                ),
            )
        )

    if id_categoria:
        consulta = consulta.filter_by(
            id_categoria=id_categoria
        )

    if estado in {
        "Vigente",
        "Archivado",
    }:
        consulta = consulta.filter_by(
            estado=estado
        )

    if nivel_acceso in {
        "direccion",
        "direccion_docentes",
    }:
        consulta = consulta.filter_by(
            nivel_acceso=nivel_acceso
        )

    documentos = (
        consulta
        .order_by(
            DocumentoInstitucional
            .fecha_documental
            .desc(),

            DocumentoInstitucional
            .id_documento
            .desc(),
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

        "documentos": [
            serializar_documento(
                documento
            )
            for documento in documentos
        ],
    }), 200


# =========================================================
# FICHA DEL DOCUMENTO
# =========================================================

@repositorio_bp.get(
    "/<int:id_documento>"
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
        or documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no existe en el repositorio."
        }), 404

    return jsonify({
        "documento":
            serializar_documento(
                documento,
                incluir_versiones=True,
            )
    }), 200


# =========================================================
# SUBIR DOCUMENTO INSTITUCIONAL
# =========================================================

@repositorio_bp.post("")
@permission_required("documentos.subir")
def crear_documento():
    id_ciclo = request.form.get(
        "id_ciclo",
        type=int,
    )

    id_categoria = request.form.get(
        "id_categoria",
        type=int,
    )

    titulo = str(
        request.form.get(
            "titulo",
            ""
        )
    ).strip()

    descripcion = str(
        request.form.get(
            "descripcion",
            ""
        )
    ).strip() or None

    nivel_acceso = str(
        request.form.get(
            "nivel_acceso",
            ""
        )
    ).strip()

    fecha_texto = str(
        request.form.get(
            "fecha_documental",
            ""
        )
    ).strip()

    archivo = request.files.get(
        "archivo"
    )

    if not id_ciclo:
        return jsonify({
            "mensaje":
                "Debe indicar el ciclo escolar."
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

    if not titulo:
        return jsonify({
            "mensaje":
                "Escriba el título del documento."
        }), 400

    categoria = db.session.get(
        CategoriaRepositorio,
        id_categoria
        if id_categoria
        else 0,
    )

    if (
        not categoria
        or not categoria.activa
    ):
        return jsonify({
            "mensaje":
                "Seleccione una categoría válida."
        }), 400

    if nivel_acceso not in {
        "direccion",
        "direccion_docentes",
    }:
        return jsonify({
            "mensaje":
                "Seleccione un nivel de acceso válido."
        }), 400

    try:
        fecha_documental = (
            date.fromisoformat(
                fecha_texto
            )
        )

    except ValueError:
        return jsonify({
            "mensaje":
                "La fecha documental no es válida."
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
        / str(ciclo.anio)
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

        documento = DocumentoInstitucional(
            codigo=
                generar_codigo_documento(
                    ciclo.anio
                ),

            id_ciclo=
                ciclo.id_ciclo,

            id_categoria=
                categoria.id_categoria,

            titulo=
                titulo,

            descripcion=
                descripcion,

            fecha_documental=
                fecha_documental,

            nivel_acceso=
                nivel_acceso,

            estado=
                "Vigente",

            version_actual=
                1,

            id_usuario_responsable=
                id_usuario,

            en_papelera=
                False,
        )

        db.session.add(
            documento
        )

        db.session.flush()

        version = (
            VersionDocumentoInstitucional(
                id_documento=
                    documento.id_documento,

                numero_version=
                    1,

                nombre_archivo=
                    datos_archivo["nombre"],

                ruta_archivo=
                    str(
                        ruta_relativa
                    ),

                tipo_mime=(
                    archivo.mimetype
                    or
                    "application/octet-stream"
                ),

                tamano_bytes=
                    datos_archivo["tamano"],

                hash_archivo=
                    hash_archivo,

                motivo=
                    "Carga inicial",

                id_usuario=
                    id_usuario,
            )
        )

        db.session.add(
            version
        )

        registrar_actividad (
            id_usuario=id_usuario,
            accion="SUBIR_DOCUMENTO",
            modulo="Repositorio institucional",
            registro=documento.codigo,
            descripcion=( 
                f"Se registro el documento institucional"
                f"«{documento.titulo}»."
            )
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Documento institucional guardado correctamente.",

            "documento":
                serializar_documento(
                    documento,
                    incluir_versiones=True,
                ),
        }), 201

    except Exception as error:
        db.session.rollback()

        if ruta_absoluta.exists():
            ruta_absoluta.unlink()

        print(
            "ERROR CREAR DOCUMENTO INSTITUCIONAL:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible guardar el documento."
        }), 500


# =========================================================
# EDITAR METADATOS
# =========================================================

@repositorio_bp.put(
    "/<int:id_documento>"
)
@permission_required("documentos.actualizar")
def actualizar_documento(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no existe en el repositorio."
        }), 404

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
            "mensaje": error
        }), 400

    data = request.get_json(
        silent=True
    ) or {}

    titulo = str(
        data.get(
            "titulo",
            documento.titulo
        )
    ).strip()

    if not titulo:
        return jsonify({
            "mensaje":
                "El título es obligatorio."
        }), 400

    id_categoria = data.get(
        "id_categoria",
        documento.id_categoria
    )

    categoria = db.session.get(
        CategoriaRepositorio,
        int(id_categoria)
        if id_categoria
        else 0,
    )

    if not categoria:
        return jsonify({
            "mensaje":
                "La categoría seleccionada no existe."
        }), 400

    estado = str(
        data.get(
            "estado",
            documento.estado
        )
    ).strip()

    if estado not in {
        "Vigente",
        "Archivado",
    }:
        return jsonify({
            "mensaje":
                "El estado seleccionado no es válido."
        }), 400

    nivel_acceso = str(
        data.get(
            "nivel_acceso",
            documento.nivel_acceso
        )
    ).strip()

    if nivel_acceso not in {
        "direccion",
        "direccion_docentes",
    }:
        return jsonify({
            "mensaje":
                "El nivel de acceso no es válido."
        }), 400

    descripcion = str(
        data.get(
            "descripcion",
            documento.descripcion or ""
        )
    ).strip() or None

    try:
        documento.titulo = titulo
        documento.id_categoria = (
            categoria.id_categoria
        )
        documento.estado = estado
        documento.nivel_acceso = (
            nivel_acceso
        )
        documento.descripcion = (
            descripcion
        )
        documento.fecha_actualizacion = (
            datetime.utcnow()
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Metadatos actualizados correctamente.",

            "documento":
                serializar_documento(
                    documento,
                    incluir_versiones=True,
                ),
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR EDITAR DOCUMENTO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible actualizar el documento."
        }), 500


# =========================================================
# REEMPLAZAR ARCHIVO / NUEVA VERSIÓN
# =========================================================

@repositorio_bp.post(
    "/<int:id_documento>/reemplazar"
)
@permission_required("documentos.actualizar")
def reemplazar_archivo(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no existe en el repositorio."
        }), 404

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
            "mensaje": error
        }), 400

    motivo = str(
        request.form.get(
            "motivo",
            ""
        )
    ).strip()

    archivo = request.files.get(
        "archivo"
    )

    if not motivo:
        return jsonify({
            "mensaje":
                "Indique el motivo del reemplazo."
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

    nueva_version = (
        documento.version_actual
        + 1
    )

    carpeta = (
        STORAGE_DIR
        / str(ciclo.anio)
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

        version = (
            VersionDocumentoInstitucional(
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
                    or
                    "application/octet-stream"
                ),

                tamano_bytes=
                    datos_archivo["tamano"],

                hash_archivo=
                    hash_archivo,

                motivo=
                    motivo,

                id_usuario=
                    id_usuario,
            )
        )

        documento.version_actual = (
            nueva_version
        )

        documento.id_usuario_responsable = (
            id_usuario
        )

        documento.fecha_actualizacion = (
            datetime.utcnow()
        )

        db.session.add(
            version
        )

        registrar_actividad ( 
            id_usuario=id_usuario,
            accion="REEMPLAZAR_DOCUMENTO",
            modulo="Repositorio institucional",
            registro=documento.codigo,
            descripcion=( 
                f"Se creó la versión {nueva_version} del documento "
                f"«{documento.titulo}». Motivo: {motivo}"
            ) 
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Nueva versión guardada correctamente.",

            "version":
                nueva_version,

            "documento":
                serializar_documento(
                    documento,
                    incluir_versiones=True,
                ),
        }), 201

    except Exception as error:
        db.session.rollback()

        if ruta_absoluta.exists():
            ruta_absoluta.unlink()

        print(
            "ERROR REEMPLAZAR ARCHIVO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible reemplazar el archivo."
        }), 500


# =========================================================
# ENVIAR A PAPELERA
# =========================================================

@repositorio_bp.patch(
    "/<int:id_documento>/papelera"
)
@permission_required("documentos.actualizar")
def enviar_a_papelera(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if not documento:
        return jsonify({
            "mensaje":
                "El documento no existe."
        }), 404

    if documento.en_papelera:
        return jsonify({
            "mensaje":
                "El documento ya se encuentra en la papelera."
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
            "mensaje": error
        }), 400

    try:
        id_usuario = int(
            get_jwt_identity()
        )

        documento.en_papelera = True

        documento.fecha_papelera = (
            datetime.utcnow()
        )

        documento.id_usuario_papelera = (
            id_usuario
        )

        documento.fecha_actualizacion = (
            datetime.utcnow()
        )

        registrar_actividad ( 
            id_usuario=id_usuario,
            accion="ENVIAR_A_PAPELERA",
            modulo="Repositorio institucional",
            registro=documento.codigo,
            descripcion=(  
                f"Se envió a la papelera el documento "
                f"«{documento.titulo}»."
            )
        )

        db.session.commit()

        return jsonify({
            "mensaje":
                "Documento enviado a la papelera correctamente."
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ENVIAR A PAPELERA:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible enviar el documento a la papelera."
        }), 500


# =========================================================
# VER ARCHIVO ACTUAL
# =========================================================

@repositorio_bp.get(
    "/<int:id_documento>/ver"
)
@permission_required("documentos.ver")
def ver_archivo(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no existe en el repositorio."
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
# DESCARGAR ARCHIVO ACTUAL
# =========================================================

@repositorio_bp.get(
    "/<int:id_documento>/descargar"
)
@permission_required("documentos.descargar")
def descargar_archivo(
    id_documento
):
    documento = db.session.get(
        DocumentoInstitucional,
        id_documento,
    )

    if (
        not documento
        or documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no existe en el repositorio."
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
# DESCARGAR UNA VERSIÓN DEL HISTORIAL
# =========================================================

@repositorio_bp.get(
    "/versiones/<int:id_version>/descargar"
)
@permission_required("documentos.descargar")
def descargar_version(
    id_version
):
    version = db.session.get(
        VersionDocumentoInstitucional,
        id_version,
    )

    if not version:
        return jsonify({
            "mensaje":
                "La versión no existe."
        }), 404

    documento = db.session.get(
        DocumentoInstitucional,
        version.id_documento,
    )

    if (
        not documento
        or documento.en_papelera
    ):
        return jsonify({
            "mensaje":
                "El documento no está disponible."
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