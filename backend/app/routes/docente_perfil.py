from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Matricula,
    Seccion,
    Usuario,
)


docente_perfil_bp = Blueprint(
    "docente_perfil",
    __name__,
    url_prefix="/api/docente/perfil",
)


EXTENSIONES_PERMITIDAS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}

MAX_FOTO_BYTES = (
    5 * 1024 * 1024
)


NOMBRES_GRADO = {
    1: "Primero",
    2: "Segundo",
    3: "Tercero",
    4: "Cuarto",
    5: "Quinto",
    6: "Sexto",
}


# =========================================================
# UTILIDADES
# =========================================================

def obtener_docente_actual():
    identidad = get_jwt_identity()

    try:
        id_usuario = int(
            identidad
        )
    except (
        TypeError,
        ValueError,
    ):
        return None

    usuario = db.session.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        return None

    if (
        not usuario.rol
        or usuario.rol.nombre.lower()
        != "docente"
    ):
        return None

    return usuario


def nombre_seccion(seccion):
    return (
        f"{NOMBRES_GRADO.get(seccion.grado, seccion.grado)} "
        f"{seccion.nombre}"
    )


def obtener_secciones(
    usuario,
    id_ciclo=None,
):
    consulta = (
        Seccion.query
        .filter_by(
            id_docente=
                usuario.id_usuario,
            activo=True,
        )
    )

    if id_ciclo:
        consulta = consulta.filter_by(
            id_ciclo=id_ciclo
        )

    secciones = (
        consulta
        .order_by(
            Seccion.grado.asc(),
            Seccion.nombre.asc(),
        )
        .all()
    )

    resultado = []

    for seccion in secciones:
        total = (
            Matricula.query
            .filter_by(
                id_ciclo=
                    seccion.id_ciclo,
                id_seccion=
                    seccion.id_seccion,
            )
            .filter(
                Matricula.estado
                != "Retirada"
            )
            .count()
        )

        resultado.append({
            "id_seccion":
                seccion.id_seccion,

            "id_ciclo":
                seccion.id_ciclo,

            "etiqueta":
                nombre_seccion(
                    seccion
                ),

            "estudiantes":
                total,
        })

    return resultado


def serializar_perfil(
    usuario,
    id_ciclo=None,
):
    return {
        "id_usuario":
            usuario.id_usuario,

        "nombres":
            usuario.nombres,

        "apellidos":
            usuario.apellidos,

        "nombre_completo":
            (
                f"{usuario.nombres} "
                f"{usuario.apellidos}"
            ).strip(),

        "correo":
            usuario.correo,

        "telefono":
            usuario.telefono,

        "fecha_nacimiento": (
            usuario.fecha_nacimiento
            .isoformat()
            if usuario.fecha_nacimiento
            else None
        ),

        "rol": (
            usuario.rol.nombre
            if usuario.rol
            else "Docente"
        ),

        "activo":
            usuario.activo,

        "foto_disponible":
            bool(
                usuario.foto_perfil
            ),

        "secciones":
            obtener_secciones(
                usuario,
                id_ciclo,
            ),
    }


def ruta_foto(usuario):
    if not usuario.foto_perfil:
        return None

    ruta = Path(
        usuario.foto_perfil
    )

    if not ruta.is_absolute():
        ruta = (
            Path(__file__)
            .resolve()
            .parents[2]
            / ruta
        )

    return ruta.resolve()


# =========================================================
# OBTENER MI PERFIL
# =========================================================

@docente_perfil_bp.get("")
@jwt_required()
def obtener_perfil():
    usuario = obtener_docente_actual()

    if not usuario:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 403

    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    return jsonify({
        "perfil":
            serializar_perfil(
                usuario,
                id_ciclo,
            )
    }), 200


# =========================================================
# ACTUALIZAR MI PERFIL
# =========================================================

@docente_perfil_bp.put("")
@jwt_required()
def actualizar_perfil():
    usuario = obtener_docente_actual()

    if not usuario:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 403

    data = request.get_json(
        silent=True
    ) or {}

    nombres = str(
        data.get(
            "nombres",
            usuario.nombres,
        )
    ).strip()

    apellidos = str(
        data.get(
            "apellidos",
            usuario.apellidos,
        )
    ).strip()

    correo = str(
        data.get(
            "correo",
            usuario.correo,
        )
    ).strip().lower()

    telefono = str(
        data.get(
            "telefono",
            usuario.telefono or "",
        )
    ).strip() or None

    if (
        not nombres
        or not apellidos
        or not correo
    ):
        return jsonify({
            "mensaje":
                "Nombre, apellidos y correo son obligatorios."
        }), 400

    correo_existente = (
        Usuario.query
        .filter(
            db.func.lower(
                Usuario.correo
            ) == correo,

            Usuario.id_usuario
            != usuario.id_usuario,
        )
        .first()
    )

    if correo_existente:
        return jsonify({
            "mensaje":
                "El correo ya pertenece a otro usuario."
        }), 400

    fecha_texto = data.get(
        "fecha_nacimiento"
    )

    fecha_nacimiento = None

    if fecha_texto:
        try:
            fecha_nacimiento = (
                date.fromisoformat(
                    fecha_texto
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            return jsonify({
                "mensaje":
                    "La fecha de nacimiento no es válida."
            }), 400

    try:
        usuario.nombres = nombres
        usuario.apellidos = apellidos
        usuario.correo = correo
        usuario.telefono = telefono
        usuario.fecha_nacimiento = (
            fecha_nacimiento
        )
        usuario.fecha_actualizacion = (
            datetime.utcnow()
        )

        db.session.commit()

        id_ciclo = data.get(
            "id_ciclo"
        )

        try:
            id_ciclo = (
                int(id_ciclo)
                if id_ciclo
                else None
            )
        except (
            TypeError,
            ValueError,
        ):
            id_ciclo = None

        return jsonify({
            "mensaje":
                "Perfil actualizado correctamente.",

            "perfil":
                serializar_perfil(
                    usuario,
                    id_ciclo,
                ),
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ACTUALIZAR PERFIL:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible actualizar el perfil."
        }), 500


# =========================================================
# CAMBIAR FOTO
# =========================================================

@docente_perfil_bp.post("/foto")
@jwt_required()
def cambiar_foto():
    usuario = obtener_docente_actual()

    if not usuario:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 403

    foto = request.files.get(
        "foto"
    )

    if not foto:
        return jsonify({
            "mensaje":
                "Seleccione una imagen."
        }), 400

    nombre_original = secure_filename(
        foto.filename or ""
    )

    if "." not in nombre_original:
        return jsonify({
            "mensaje":
                "El archivo seleccionado no es válido."
        }), 400

    extension = (
        nombre_original
        .rsplit(".", 1)[1]
        .lower()
    )

    if (
        extension
        not in EXTENSIONES_PERMITIDAS
    ):
        return jsonify({
            "mensaje":
                "La foto debe ser PNG, JPG, JPEG o WEBP."
        }), 400

    foto.stream.seek(
        0,
        2,
    )

    tamano = foto.stream.tell()

    foto.stream.seek(0)

    if tamano > MAX_FOTO_BYTES:
        return jsonify({
            "mensaje":
                "La fotografía no puede superar 5 MB."
        }), 400

    carpeta = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "storage"
        / "perfiles"
    )

    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )

    nombre_nuevo = (
        f"{uuid4().hex}."
        f"{extension}"
    )

    destino = (
        carpeta
        / nombre_nuevo
    )

    ruta_anterior = (
        ruta_foto(usuario)
    )

    try:
        foto.save(
            destino
        )

        usuario.foto_perfil = str(
            Path(
                "storage",
                "perfiles",
                nombre_nuevo,
            )
        )

        usuario.fecha_actualizacion = (
            datetime.utcnow()
        )

        db.session.commit()

        if (
            ruta_anterior
            and ruta_anterior.exists()
            and ruta_anterior.is_file()
            and ruta_anterior != destino
        ):
            try:
                ruta_anterior.unlink()
            except OSError:
                pass

        return jsonify({
            "mensaje":
                "Foto de perfil actualizada correctamente."
        }), 200

    except Exception as error:
        db.session.rollback()

        if destino.exists():
            try:
                destino.unlink()
            except OSError:
                pass

        print(
            "ERROR FOTO PERFIL:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible actualizar la foto."
        }), 500


# =========================================================
# OBTENER FOTO
# =========================================================

@docente_perfil_bp.get("/foto")
@jwt_required()
def obtener_foto():
    usuario = obtener_docente_actual()

    if not usuario:
        return jsonify({
            "mensaje":
                "No fue posible identificar al docente."
        }), 403

    ruta = ruta_foto(
        usuario
    )

    if (
        not ruta
        or not ruta.exists()
        or not ruta.is_file()
    ):
        return jsonify({
            "mensaje":
                "El docente no tiene una foto de perfil."
        }), 404

    return send_file(
        ruta,
        as_attachment=False,
    )