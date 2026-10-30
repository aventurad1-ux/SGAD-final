from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import (
    CicloEscolar,
    Permiso,
    Role,
    Seccion,
    Usuario,
    UsuarioPermiso,
)
from app.services.password_service import hash_password
from app.services.hibp_service import (
    HIBPServiceError,
    verificar_password_comprometida,
)
from app.services.bitacora_service import registrar_actividad
from app.utils.permissions import permission_required


usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/api/directora/usuarios",
)


# =========================================================
# UTILIDADES
# =========================================================

def nombre_usuario(usuario):
    return (
        f"{usuario.nombres or ''} "
        f"{usuario.apellidos or ''}"
    ).strip()


def nombre_seccion(seccion):
    nombres_grado = {
        1: "Primero",
        2: "Segundo",
        3: "Tercero",
        4: "Cuarto",
        5: "Quinto",
        6: "Sexto",
    }

    return (
        f"{nombres_grado.get(seccion.grado, seccion.grado)} "
        f"{seccion.nombre}"
    )


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


def obtener_permisos_rol(usuario):
    if not usuario.rol:
        return set()

    return {
        permiso.codigo
        for permiso in usuario.rol.permisos
        if permiso.activo
    }


def obtener_excepciones_usuario(usuario):
    return {
        item.permiso.codigo:
            item.permitido
        for item in usuario.permisos_individuales
        if item.permiso
        and item.permiso.activo
    }


def obtener_permisos_efectivos(usuario):
    permisos_rol = obtener_permisos_rol(
        usuario
    )

    excepciones = obtener_excepciones_usuario(
        usuario
    )

    permisos_activos = set(
        permisos_rol
    )

    for codigo, permitido in excepciones.items():
        if permitido:
            permisos_activos.add(
                codigo
            )
        else:
            permisos_activos.discard(
                codigo
            )

    return permisos_activos


def secciones_usuario(
    usuario,
    ciclo
):
    if (
        not ciclo
        or not usuario
        or not usuario.rol
        or usuario.rol.nombre.lower()
        != "docente"
    ):
        return []

    return (
        Seccion.query
        .filter_by(
            id_ciclo=ciclo.id_ciclo,
            id_docente=usuario.id_usuario,
            activo=True,
        )
        .order_by(
            Seccion.grado.asc(),
            Seccion.nombre.asc(),
        )
        .all()
    )


def serializar_usuario(
    usuario,
    ciclo
):
    secciones = secciones_usuario(
        usuario,
        ciclo
    )

    if (
        usuario.rol
        and usuario.rol.nombre.lower()
        == "directora"
    ):
        alcance = (
            "Todo el establecimiento"
        )

    elif secciones:
        alcance = " y ".join(
            nombre_seccion(seccion)
            for seccion in secciones
        )

    else:
        alcance = (
            "Sin sección asignada"
        )

    permisos_rol = obtener_permisos_rol(
        usuario
    )

    excepciones = obtener_excepciones_usuario(
        usuario
    )

    permisos_efectivos = (
        obtener_permisos_efectivos(
            usuario
        )
    )

    return {
        "id_usuario":
            usuario.id_usuario,

        "nombres":
            usuario.nombres,

        "apellidos":
            usuario.apellidos,

        "nombre":
            nombre_usuario(
                usuario
            ),

        "correo":
            usuario.correo,

        "telefono":
            usuario.telefono,

        "activo":
            usuario.activo,

        "id_rol":
            usuario.id_rol,

        "rol":
            (
                usuario.rol.nombre
                if usuario.rol
                else "Sin rol"
            ),

        "alcance":
            alcance,

        "secciones": [
            {
                "id_seccion":
                    seccion.id_seccion,

                "etiqueta":
                    nombre_seccion(
                        seccion
                    ),
            }
            for seccion in secciones
        ],

        "permisos_rol":
            sorted(
                permisos_rol
            ),

        "permisos_individuales":
            excepciones,

        "permisos_efectivos":
            sorted(
                permisos_efectivos
            ),

        "fecha_creacion": (
            usuario.fecha_creacion.isoformat()
            if usuario.fecha_creacion
            else None
        ),
    }


def validar_rol(
    id_rol
):
    try:
        id_rol = int(
            id_rol
        )
    except (
        TypeError,
        ValueError
    ):
        return None

    rol = db.session.get(
        Role,
        id_rol,
    )

    if (
        not rol
        or not rol.activo
    ):
        return None

    return rol


def validar_secciones(
    ids_secciones,
    ciclo,
    usuario=None
):
    if not ids_secciones:
        return [], None

    try:
        ids = [
            int(id_seccion)
            for id_seccion
            in ids_secciones
        ]

    except (
        TypeError,
        ValueError
    ):
        return (
            [],
            "Las secciones seleccionadas no son válidas."
        )

    secciones = (
        Seccion.query
        .filter(
            Seccion.id_seccion.in_(
                ids
            ),
            Seccion.id_ciclo
            == ciclo.id_ciclo,
            Seccion.activo.is_(True),
        )
        .all()
    )

    if len(secciones) != len(
        set(ids)
    ):
        return (
            [],
            "Una de las secciones seleccionadas no existe."
        )

    conflictos = []

    for seccion in secciones:
        if (
            seccion.id_docente
            and (
                not usuario
                or seccion.id_docente
                != usuario.id_usuario
            )
        ):
            conflictos.append(
                seccion
            )

    if conflictos:
        detalles = "; ".join(
            (
                f"{nombre_seccion(seccion)} "
                f"ya tiene responsable"
            )
            for seccion
            in conflictos
        )

        return (
            [],
            (
                "No fue posible asignar: "
                f"{detalles}."
            )
        )

    return secciones, None


def aplicar_secciones(
    usuario,
    ciclo,
    secciones_nuevas
):
    secciones_actuales = (
        Seccion.query
        .filter_by(
            id_ciclo=
                ciclo.id_ciclo,

            id_docente=
                usuario.id_usuario,
        )
        .all()
    )

    ids_nuevas = {
        seccion.id_seccion
        for seccion
        in secciones_nuevas
    }

    for seccion in secciones_actuales:
        if (
            seccion.id_seccion
            not in ids_nuevas
        ):
            seccion.id_docente = None

    for seccion in secciones_nuevas:
        seccion.id_docente = (
            usuario.id_usuario
        )


def aplicar_permisos_individuales(
    usuario,
    codigos_seleccionados
):
    permisos_activos = (
        Permiso.query
        .filter_by(
            activo=True
        )
        .all()
    )

    codigos_validos = {
        permiso.codigo
        for permiso
        in permisos_activos
    }

    seleccionados = {
        str(codigo)
        for codigo
        in (
            codigos_seleccionados
            or []
        )
        if str(codigo)
        in codigos_validos
    }

    permisos_rol = (
        obtener_permisos_rol(
            usuario
        )
    )

    existentes = {
        item.id_permiso:
            item
        for item
        in usuario.permisos_individuales
    }

    for permiso in permisos_activos:
        efectivo_deseado = (
            permiso.codigo
            in seleccionados
        )

        valor_rol = (
            permiso.codigo
            in permisos_rol
        )

        excepcion = (
            existentes.get(
                permiso.id_permiso
            )
        )

        # Si coincide con lo que ya da el rol,
        # no necesitamos una excepción.
        if efectivo_deseado == valor_rol:
            if excepcion:
                db.session.delete(
                    excepcion
                )

            continue

        # Si es distinto al rol, guardamos
        # una excepción individual.
        if excepcion:
            excepcion.permitido = (
                efectivo_deseado
            )

            excepcion.fecha_asignacion = (
                datetime.utcnow()
            )

        else:
            db.session.add(
                UsuarioPermiso(
                    id_usuario=
                        usuario.id_usuario,

                    id_permiso=
                        permiso.id_permiso,

                    permitido=
                        efectivo_deseado,
                )
            )


# =========================================================
# LISTAR USUARIOS
# =========================================================

@usuarios_bp.get("")
@permission_required(
    "usuarios.ver"
)
def listar_usuarios():
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

    usuarios = (
        Usuario.query
        .join(Role)
        .order_by(
            Role.nombre.asc(),
            Usuario.nombres.asc(),
            Usuario.apellidos.asc(),
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

        "usuarios": [
            serializar_usuario(
                usuario,
                ciclo
            )
            for usuario
            in usuarios
        ],
    }), 200


# =========================================================
# CATÁLOGOS
# =========================================================

@usuarios_bp.get(
    "/catalogos"
)
@permission_required(
    "usuarios.ver"
)
def catalogos_usuarios():
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

    roles = (
        Role.query
        .filter_by(
            activo=True
        )
        .order_by(
            Role.nombre.asc()
        )
        .all()
    )

    permisos = (
        Permiso.query
        .filter_by(
            activo=True
        )
        .order_by(
            Permiso.modulo.asc(),
            Permiso.nombre.asc(),
        )
        .all()
    )

    secciones = (
        Seccion.query
        .filter_by(
            id_ciclo=
                ciclo.id_ciclo,

            activo=True,
        )
        .order_by(
            Seccion.grado.asc(),
            Seccion.nombre.asc(),
        )
        .all()
    )

    return jsonify({
        "roles": [
            {
                "id_rol":
                    rol.id_rol,

                "nombre":
                    rol.nombre,

                "descripcion":
                    rol.descripcion,
                "permisos": [
                    permiso.codigo
                    for permiso
                    in rol.permisos
                    if permiso.activo
                ]
            }
            for rol in roles
        ],

        "permisos": [
            {
                "id_permiso":
                    permiso.id_permiso,

                "codigo":
                    permiso.codigo,

                "nombre":
                    permiso.nombre,

                "descripcion":
                    permiso.descripcion,

                "modulo":
                    permiso.modulo,
            }
            for permiso in permisos
        ],

        "secciones": [
            {
                "id_seccion":
                    seccion.id_seccion,

                "etiqueta":
                    nombre_seccion(
                        seccion
                    ),

                "id_docente":
                    seccion.id_docente,

                "docente": (
                    nombre_usuario(
                        seccion.docente
                    )
                    if seccion.docente
                    else None
                ),
            }
            for seccion in secciones
        ],
    }), 200


# =========================================================
# CREAR USUARIO
# =========================================================

@usuarios_bp.post("")
@permission_required(
    "usuarios.crear"
)
def crear_usuario():
    data = request.get_json(
        silent=True
    ) or {}

    id_ciclo = data.get(
        "id_ciclo"
    )

    ciclo = obtener_ciclo(
        int(id_ciclo)
        if id_ciclo
        else None
    )

    if not ciclo:
        return jsonify({
            "mensaje":
                "El ciclo escolar no existe."
        }), 404

    if ciclo.estado != "activo":
        return jsonify({
            "mensaje":
                (
                    "Seleccione el ciclo activo "
                    "para administrar usuarios."
                )
        }), 400

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

    correo = str(
        data.get(
            "correo",
            ""
        )
    ).strip().lower()

    telefono = str(
        data.get(
            "telefono",
            ""
        )
    ).strip() or None

    password = str(
        data.get(
            "password",
            ""
        )
    )

    rol = validar_rol(
        data.get(
            "id_rol"
        )
    )

    if (
        not nombres
        or not apellidos
        or not correo
    ):
        return jsonify({
            "mensaje":
                (
                    "Nombres, apellidos y correo "
                    "son obligatorios."
                )
        }), 400

    if not rol:
        return jsonify({
            "mensaje":
                "Seleccione un rol válido."
        }), 400

    if len(password) < 10:
        return jsonify({
            "mensaje":
                (
                    "La contraseña temporal debe "
                    "tener al menos 10 caracteres."
                )
        }), 400

    try:
        resultado_hibp = (
            verificar_password_comprometida(
                password
            )
        )

    except HIBPServiceError:
        return jsonify({
            "mensaje":
                (
                    "No fue posible verificar "
                    "la seguridad de la contraseña. "
                    "Intente nuevamente."
                )
        }), 503

    if resultado_hibp["comprometida"]:
        return jsonify({
            "mensaje":
                (
                    "La contraseña seleccionada aparece "
                    "en filtraciones de datos conocidas. "
                    "Utilice una contraseña diferente."
                ),
            "codigo":
                "PASSWORD_COMPROMETIDA",
            "apariciones":
                resultado_hibp["apariciones"],
        }), 400

    correo_existente = (
        Usuario.query
        .filter(
            db.func.lower(
                Usuario.correo
            ) == correo
        )
        .first()
    )

    if correo_existente:
        return jsonify({
            "mensaje":
                (
                    "El correo ya pertenece "
                    "a otro usuario."
                )
        }), 400

    ids_secciones = (
        data.get(
            "secciones"
        )
        or []
    )

    if (
        rol.nombre.lower()
        == "docente"
    ):
        secciones, error = (
            validar_secciones(
                ids_secciones,
                ciclo,
            )
        )

        if error:
            return jsonify({
                "mensaje":
                    error
            }), 400

    else:
        secciones = []

    try:
        usuario = Usuario(
            id_rol=
                rol.id_rol,

            nombres=
                nombres,

            apellidos=
                apellidos,

            correo=
                correo,

            telefono=
                telefono,

            contrasena_hash=
                hash_password(
                    password
                ),

            activo=bool(
                data.get(
                    "activo",
                    True
                )
            ),
        )

        db.session.add(
            usuario
        )

        db.session.flush()

        if (
            rol.nombre.lower()
            == "docente"
        ):
            aplicar_secciones(
                usuario,
                ciclo,
                secciones,
            )

            aplicar_permisos_individuales(
                usuario,
                data.get(
                    "permisos"
                )
                or []
            )

        registrar_actividad(
            id_usuario=int(get_jwt_identity()),
            accion="CREAR_USUARIO",
            modulo="Usuarios",
            descripcion=(
                f"Se creó el usuario "
                f"{usuario.nombres} {usuario.apellidos} "
                f"(ID: {usuario.id_usuario})."
            )
        )


        db.session.commit()

        return jsonify({
            "mensaje":
                (
                    "Usuario y asignaciones "
                    "guardados correctamente."
                ),

            "usuario":
                serializar_usuario(
                    usuario,
                    ciclo
                ),
        }), 201

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CREAR USUARIO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible crear el usuario."
        }), 500


# =========================================================
# ACTUALIZAR USUARIO
# =========================================================

@usuarios_bp.put(
    "/<int:id_usuario>"
)
@permission_required(
    "usuarios.editar"
)
def actualizar_usuario(
    id_usuario
):
    usuario = db.session.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        return jsonify({
            "mensaje":
                "El usuario no existe."
        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    id_ciclo = data.get(
        "id_ciclo"
    )

    ciclo = obtener_ciclo(
        int(id_ciclo)
        if id_ciclo
        else None
    )

    if not ciclo:
        return jsonify({
            "mensaje":
                "El ciclo escolar no existe."
        }), 404

    if ciclo.estado != "activo":
        return jsonify({
            "mensaje":
                (
                    "Seleccione el ciclo activo "
                    "para administrar usuarios."
                )
        }), 400

    usuario_actual_id = int(
        get_jwt_identity()
    )

    nombres = str(
        data.get(
            "nombres",
            usuario.nombres
        )
    ).strip()

    apellidos = str(
        data.get(
            "apellidos",
            usuario.apellidos
        )
    ).strip()

    correo = str(
        data.get(
            "correo",
            usuario.correo
        )
    ).strip().lower()

    telefono = str(
        data.get(
            "telefono",
            usuario.telefono or ""
        )
    ).strip() or None

    if (
        not nombres
        or not apellidos
        or not correo
    ):
        return jsonify({
            "mensaje":
                (
                    "Nombres, apellidos y correo "
                    "son obligatorios."
                )
        }), 400

    otro_correo = (
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

    if otro_correo:
        return jsonify({
            "mensaje":
                (
                    "El correo ya pertenece "
                    "a otro usuario."
                )
        }), 400

    es_cuenta_actual = (
        usuario.id_usuario
        == usuario_actual_id
    )

    rol_actual_directora = (
        usuario.rol
        and usuario.rol.nombre.lower()
        == "directora"
    )

    if (
        es_cuenta_actual
        or rol_actual_directora
    ):
        rol = usuario.rol

    else:
        rol = validar_rol(
            data.get(
                "id_rol",
                usuario.id_rol
            )
        )

        if not rol:
            return jsonify({
                "mensaje":
                    "Seleccione un rol válido."
            }), 400

    ids_secciones = (
        data.get(
            "secciones"
        )
        or []
    )

    if (
        rol
        and rol.nombre.lower()
        == "docente"
    ):
        secciones, error = (
            validar_secciones(
                ids_secciones,
                ciclo,
                usuario,
            )
        )

        if error:
            return jsonify({
                "mensaje":
                    error
            }), 400

    else:
        secciones = []

    try:
        usuario.nombres = nombres
        usuario.apellidos = apellidos
        usuario.correo = correo
        usuario.telefono = telefono
        usuario.id_rol = rol.id_rol
        usuario.fecha_actualizacion = (
            datetime.utcnow()
        )

        password = str(
            data.get(
                "password",
                ""
            )
        )

        if password:
            if len(password) < 10:
                return jsonify({
                    "mensaje":
                        (
                            "La nueva contraseña debe "
                            "tener al menos 10 caracteres."
                        )
                }), 400

            try:
                resultado_hibp = (
                    verificar_password_comprometida(
                        password
                    )
                )

            except HIBPServiceError:
                return jsonify({
                    "mensaje":
                        (
                            "No fue posible verificar "
                            "la seguridad de la contraseña. "
                            "Intente nuevamente."
                        )
                }), 503

            if resultado_hibp["comprometida"]:
                return jsonify({
                    "mensaje":
                        (
                            "La contraseña seleccionada aparece "
                            "en filtraciones de datos conocidas. "
                            "Utilice una contraseña diferente."
                        ),
                    "codigo":
                        "PASSWORD_COMPROMETIDA",
                    "apariciones":
                        resultado_hibp["apariciones"],
                }), 400

            usuario.contrasena_hash = (
                hash_password(
                    password
                )
            )

        if (
            rol.nombre.lower()
            == "docente"
        ):
            aplicar_secciones(
                usuario,
                ciclo,
                secciones,
            )

            aplicar_permisos_individuales(
                usuario,
                data.get(
                    "permisos"
                )
                or []
            )

        else:
            aplicar_secciones(
                usuario,
                ciclo,
                [],
            )

            # La cuenta de Dirección utiliza
            # los permisos de su rol.
            for excepcion in list(
                usuario.permisos_individuales
            ):
                db.session.delete(
                    excepcion
                )

        db.session.commit()

        return jsonify({
            "mensaje":
                (
                    "Usuario y asignaciones "
                    "actualizados correctamente."
                ),

            "usuario":
                serializar_usuario(
                    usuario,
                    ciclo
                ),
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ACTUALIZAR USUARIO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible actualizar el usuario."
        }), 500


# =========================================================
# ACTIVAR / DESACTIVAR
# =========================================================

@usuarios_bp.patch(
    "/<int:id_usuario>/estado"
)
@permission_required(
    "usuarios.eliminar"
)
def cambiar_estado_usuario(
    id_usuario
):
    usuario = db.session.get(
        Usuario,
        id_usuario,
    )

    if not usuario:
        return jsonify({
            "mensaje":
                "El usuario no existe."
        }), 404

    usuario_actual_id = int(
        get_jwt_identity()
    )

    if (
        usuario.id_usuario
        == usuario_actual_id
    ):
        return jsonify({
            "mensaje":
                (
                    "No puede desactivar "
                    "su propia cuenta."
                )
        }), 400

    data = request.get_json(
        silent=True
    ) or {}

    if "activo" not in data:
        return jsonify({
            "mensaje":
                "Indique el estado del usuario."
        }), 400

    try:
        usuario.activo = bool(
            data.get(
                "activo"
            )
        )

        usuario.fecha_actualizacion = (
            datetime.utcnow()
        )

        db.session.commit()

        return jsonify({
            "mensaje": (
                "Usuario activado correctamente."
                if usuario.activo
                else
                "Usuario desactivado correctamente."
            ),

            "activo":
                usuario.activo,
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR ESTADO USUARIO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                (
                    "No fue posible cambiar "
                    "el estado del usuario."
                )
        }), 500