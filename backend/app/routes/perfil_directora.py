
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Usuario


perfil_directora_bp = Blueprint(
    "perfil_directora",
    __name__,
    url_prefix="/api/directora/perfil"
)

EXTENSIONES = {"jpg", "jpeg", "png", "webp"}
MAX_FOTO = 5 * 1024 * 1024

CARPETA_FOTOS = (
    Path(__file__).resolve().parents[2]
    / "storage"
    / "perfiles"
).resolve()


def directora_actual():
    try:
        usuario_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    usuario = db.session.get(Usuario, usuario_id)

    if not usuario or not usuario.rol or not usuario.activo:
        return None

    if usuario.rol.nombre.strip().casefold() != "directora":
        return None

    return usuario


def datos_perfil(usuario):
    return {
        "id_usuario": usuario.id_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "nombre_completo": (
            f"{usuario.nombres} {usuario.apellidos}".strip()
        ),
        "correo": usuario.correo,
        "telefono": usuario.telefono,
        "fecha_nacimiento": (
            usuario.fecha_nacimiento.isoformat()
            if usuario.fecha_nacimiento else None
        ),
        "rol": usuario.rol.nombre,
        "activo": usuario.activo,
        "foto_disponible": bool(usuario.foto_perfil)
    }


def archivo_foto(usuario):
    if not usuario.foto_perfil:
        return None

    ruta = (
        Path(__file__).resolve().parents[2]
        / usuario.foto_perfil
    ).resolve()

    # Solo permitir acceso a archivos del directorio de perfiles.
    if not ruta.is_relative_to(CARPETA_FOTOS):
        return None

    return ruta


# CONSULTAR PERFIL
@perfil_directora_bp.get("")
@jwt_required()
def obtener_perfil_directora():
    usuario = directora_actual()

    if usuario is None:
        return jsonify({
            "mensaje": "No tiene permiso para consultar este perfil."
        }), 403

    return jsonify({
        "perfil": datos_perfil(usuario)
    }), 200


# EDITAR PERFIL
@perfil_directora_bp.put("")
@jwt_required()
def actualizar_perfil_directora():
    usuario = directora_actual()

    if usuario is None:
        return jsonify({
            "mensaje": "No tiene permiso para editar este perfil."
        }), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "mensaje": "Los datos enviados no son válidos."
        }), 400

    nombres = str(data.get("nombres") or "").strip()
    apellidos = str(data.get("apellidos") or "").strip()
    correo = str(data.get("correo") or "").strip().lower()
    telefono = str(data.get("telefono") or "").strip()

    if not nombres or not apellidos or not correo:
        return jsonify({
            "mensaje": "Nombre, apellidos y correo son obligatorios."
        }), 400

    if (
        len(nombres) > 100
        or len(apellidos) > 100
        or len(correo) > 150
        or len(telefono) > 20
    ):
        return jsonify({
            "mensaje": "Uno de los campos supera la longitud permitida."
        }), 400

    if "@" not in correo or "." not in correo.split("@")[-1]:
        return jsonify({
            "mensaje": "Ingrese un correo electrónico válido."
        }), 400

    correo_existente = Usuario.query.filter(
        db.func.lower(Usuario.correo) == correo,
        Usuario.id_usuario != usuario.id_usuario
    ).first()

    if correo_existente:
        return jsonify({
            "mensaje": "El correo ya pertenece a otro usuario."
        }), 400

    fecha_texto = data.get("fecha_nacimiento")
    fecha = None

    if fecha_texto:
        try:
            fecha = date.fromisoformat(fecha_texto)
        except (ValueError, TypeError):
            return jsonify({
                "mensaje": "La fecha de nacimiento no es válida."
            }), 400

        if fecha > date.today():
            return jsonify({
                "mensaje": "La fecha de nacimiento no puede ser futura."
            }), 400

    try:
        usuario.nombres = nombres
        usuario.apellidos = apellidos
        usuario.correo = correo
        usuario.telefono = telefono or None
        usuario.fecha_nacimiento = fecha
        usuario.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "mensaje": "Perfil actualizado correctamente.",
            "perfil": datos_perfil(usuario)
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "mensaje": "El correo ya pertenece a otro usuario."
        }), 409

    except Exception:
        db.session.rollback()
        return jsonify({
            "mensaje": "No fue posible actualizar el perfil."
        }), 500


# CAMBIAR FOTOGRAFÍA
@perfil_directora_bp.post("/foto")
@jwt_required()
def cambiar_foto_directora():
    usuario = directora_actual()

    if usuario is None:
        return jsonify({
            "mensaje": "No tiene permiso para cambiar esta fotografía."
        }), 403

    foto = request.files.get("foto")

    if not foto or not foto.filename:
        return jsonify({
            "mensaje": "Seleccione una imagen."
        }), 400

    nombre = secure_filename(foto.filename)

    if "." not in nombre:
        return jsonify({
            "mensaje": "El archivo seleccionado no es válido."
        }), 400

    extension = nombre.rsplit(".", 1)[1].lower()

    if extension not in EXTENSIONES:
        return jsonify({
            "mensaje": "La foto debe ser PNG, JPG, JPEG o WEBP."
        }), 400

    # Leer como máximo 5 MB + 1 byte.
    contenido = foto.stream.read(MAX_FOTO + 1)

    if len(contenido) > MAX_FOTO:
        return jsonify({
            "mensaje": "La fotografía no puede superar 5 MB."
        }), 400

    # Validar la firma del archivo, no solo su extensión.
    es_png = contenido.startswith(b"\x89PNG\r\n\x1a\n")
    es_jpeg = contenido.startswith(b"\xff\xd8\xff")
    es_webp = (
        contenido[:4] == b"RIFF"
        and contenido[8:12] == b"WEBP"
    )

    valido = (
        (extension == "png" and es_png)
        or (extension in {"jpg", "jpeg"} and es_jpeg)
        or (extension == "webp" and es_webp)
    )

    if not valido:
        return jsonify({
            "mensaje": "El contenido no corresponde a una imagen válida."
        }), 400

    CARPETA_FOTOS.mkdir(parents=True, exist_ok=True)

    destino = CARPETA_FOTOS / f"{uuid4().hex}.{extension}"
    anterior = archivo_foto(usuario)

    try:
        destino.write_bytes(contenido)

        usuario.foto_perfil = str(
            Path("storage") / "perfiles" / destino.name
        )
        usuario.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        if anterior and anterior.is_file() and anterior != destino:
            try:
                anterior.unlink()
            except OSError:
                pass

        return jsonify({
            "mensaje": "Foto de perfil actualizada correctamente.",
            "perfil": datos_perfil(usuario)
        }), 200

    except Exception:
        db.session.rollback()
        destino.unlink(missing_ok=True)

        return jsonify({
            "mensaje": "No fue posible actualizar la foto."
        }), 500


# CONSULTAR FOTOGRAFÍA
@perfil_directora_bp.get("/foto")
@jwt_required()
def obtener_foto_directora():
    usuario = directora_actual()

    if usuario is None:
        return jsonify({
            "mensaje": "No tiene permiso para consultar esta fotografía."
        }), 403

    ruta = archivo_foto(usuario)

    if ruta is None or not ruta.is_file():
        return jsonify({
            "mensaje": "No hay fotografía de perfil."
        }), 404

    return send_file(ruta, as_attachment=False)


# QUITAR FOTOGRAFÍA
@perfil_directora_bp.delete("/foto")
@jwt_required()
def quitar_foto_directora():
    usuario = directora_actual()

    if usuario is None:
        return jsonify({
            "mensaje": "No tiene permiso para eliminar esta fotografía."
        }), 403

    anterior = archivo_foto(usuario)

    try:
        usuario.foto_perfil = None
        usuario.fecha_actualizacion = datetime.utcnow()
        db.session.commit()

        if anterior and anterior.is_file():
            try:
                anterior.unlink()
            except OSError:
                pass

        return jsonify({
            "mensaje": "Fotografía eliminada. Se muestran las iniciales.",
            "perfil": datos_perfil(usuario)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "mensaje": "No fue posible quitar la fotografía."
        }), 500
