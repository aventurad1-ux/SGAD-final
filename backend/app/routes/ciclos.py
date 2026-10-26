from datetime import date

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import (
    CicloEscolar,
    Matricula,
    Role,
    Seccion,
    Usuario,
)
from app.utils.permissions import permission_required


ciclos_bp = Blueprint(
    "ciclos",
    __name__,
    url_prefix="/api/directora/ciclos",
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

def nombre_usuario(usuario):
    if not usuario:
        return "Sin responsable"

    return (
        f"{usuario.nombres or ''} "
        f"{usuario.apellidos or ''}"
    ).strip()


def etiqueta_seccion(seccion):
    return (
        f"{NOMBRES_GRADO.get(seccion.grado, seccion.grado)} "
        f"{seccion.nombre}"
    )


def serializar_ciclo(ciclo):
    return {
        "id_ciclo": ciclo.id_ciclo,
        "anio": ciclo.anio,
        "fecha_inicio": (
            ciclo.fecha_inicio.isoformat()
            if ciclo.fecha_inicio
            else None
        ),
        "fecha_fin": (
            ciclo.fecha_fin.isoformat()
            if ciclo.fecha_fin
            else None
        ),
        "estado": ciclo.estado,
        "editable": ciclo.estado == "activo",
    }


def serializar_seccion(seccion):
    total = (
        Matricula.query
        .filter_by(
            id_ciclo=seccion.id_ciclo,
            id_seccion=seccion.id_seccion,
        )
        .filter(
            Matricula.estado != "Retirada"
        )
        .count()
    )

    return {
        "id_seccion": seccion.id_seccion,
        "grado": seccion.grado,
        "nombre": seccion.nombre,
        "etiqueta": etiqueta_seccion(seccion),
        "id_docente": seccion.id_docente,
        "docente": nombre_usuario(
            seccion.docente
        ),
        "activo": seccion.activo,
        "estudiantes": total,
    }


def obtener_docentes():
    rol_docente = (
        Role.query
        .filter(
            db.func.lower(Role.nombre)
            == "docente"
        )
        .first()
    )

    if not rol_docente:
        return []

    return (
        Usuario.query
        .filter_by(
            id_rol=rol_docente.id_rol,
            activo=True,
        )
        .order_by(
            Usuario.nombres.asc(),
            Usuario.apellidos.asc(),
        )
        .all()
    )


def obtener_ciclo_base():
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


def crear_seccion_promocion(
    nuevo_ciclo,
    grado,
    nombre
):
    nueva = Seccion(
        id_ciclo=nuevo_ciclo.id_ciclo,
        grado=grado,
        nombre=nombre.upper(),
        id_docente=None,
        activo=True,
    )

    db.session.add(nueva)
    db.session.flush()

    return nueva


# =========================================================
# CONSULTAR CICLOS
# =========================================================

@ciclos_bp.get("")
@permission_required("estudiantes.ver")
def listar_ciclos():
    id_ciclo = request.args.get(
        "id_ciclo",
        type=int,
    )

    if id_ciclo:
        ciclo = db.session.get(
            CicloEscolar,
            id_ciclo,
        )
    else:
        ciclo = (
            CicloEscolar.query
            .order_by(
                CicloEscolar.anio.desc()
            )
            .first()
        )

    if not ciclo:
        return jsonify({
            "mensaje":
                "No existen ciclos escolares."
        }), 404

    secciones = (
        Seccion.query
        .filter_by(
            id_ciclo=ciclo.id_ciclo
        )
        .order_by(
            Seccion.grado.asc(),
            Seccion.nombre.asc(),
        )
        .all()
    )

    ciclos = (
        CicloEscolar.query
        .order_by(
            CicloEscolar.anio.desc()
        )
        .all()
    )

    return jsonify({
        "ciclo":
            serializar_ciclo(ciclo),

        "ciclos": [
            serializar_ciclo(item)
            for item in ciclos
        ],

        "secciones": [
            serializar_seccion(seccion)
            for seccion in secciones
        ],
    }), 200


# =========================================================
# CATÁLOGOS
# =========================================================

@ciclos_bp.get("/catalogos")
@permission_required("estudiantes.ver")
def catalogos_ciclo():
    docentes = obtener_docentes()

    return jsonify({
        "docentes": [
            {
                "id_usuario":
                    docente.id_usuario,

                "nombre":
                    nombre_usuario(docente),
            }
            for docente in docentes
        ]
    }), 200


# =========================================================
# CREAR SECCIÓN
# =========================================================

@ciclos_bp.post("/secciones")
@permission_required("estudiantes.ver")
def crear_seccion():
    data = request.get_json() or {}

    id_ciclo = data.get(
        "id_ciclo"
    )

    grado = data.get(
        "grado"
    )

    nombre = str(
        data.get(
            "nombre",
            ""
        )
    ).strip().upper()

    id_docente = data.get(
        "id_docente"
    )

    try:
        id_ciclo = int(id_ciclo)

    except (
        TypeError,
        ValueError
    ):
        return jsonify({
            "mensaje":
                "Seleccione un ciclo escolar válido."
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

    if ciclo.estado != "activo":
        return jsonify({
            "mensaje":
                "No puede modificar un ciclo histórico."
        }), 400

    try:
        grado = int(grado)

    except (
        TypeError,
        ValueError
    ):
        return jsonify({
            "mensaje":
                "Seleccione un grado válido."
        }), 400

    if grado < 1 or grado > 6:
        return jsonify({
            "mensaje":
                "Seleccione un grado válido."
        }), 400

    if not nombre:
        return jsonify({
            "mensaje":
                "Ingrese la sección."
        }), 400

    existente = (
        Seccion.query
        .filter_by(
            id_ciclo=ciclo.id_ciclo,
            grado=grado,
            nombre=nombre,
        )
        .first()
    )

    if existente:
        return jsonify({
            "mensaje": (
                f"La sección "
                f"{NOMBRES_GRADO[grado]} "
                f"{nombre} ya existe."
            )
        }), 400

    docente = None

    if id_docente:
        try:
            docente = db.session.get(
                Usuario,
                int(id_docente),
            )

        except (
            TypeError,
            ValueError
        ):
            docente = None

        if (
            not docente
            or not docente.activo
        ):
            return jsonify({
                "mensaje":
                    "El docente seleccionado no es válido."
            }), 400

    try:
        seccion = Seccion(
            id_ciclo=ciclo.id_ciclo,
            grado=grado,
            nombre=nombre,
            id_docente=(
                docente.id_usuario
                if docente
                else None
            ),
            activo=True,
        )

        db.session.add(seccion)
        db.session.commit()

        return jsonify({
            "mensaje":
                "Sección agregada correctamente.",

            "seccion":
                serializar_seccion(seccion),
        }), 201

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CREAR SECCIÓN:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible crear la sección."
        }), 500


# =========================================================
# RESPONSABLE
# =========================================================

@ciclos_bp.put(
    "/secciones/<int:id_seccion>/responsable"
)
@permission_required("estudiantes.ver")
def asignar_responsable(id_seccion):
    seccion = db.session.get(
        Seccion,
        id_seccion,
    )

    if not seccion:
        return jsonify({
            "mensaje":
                "La sección no existe."
        }), 404

    ciclo = db.session.get(
        CicloEscolar,
        seccion.id_ciclo,
    )

    if (
        not ciclo
        or ciclo.estado != "activo"
    ):
        return jsonify({
            "mensaje":
                "No puede modificar un ciclo histórico."
        }), 400

    data = request.get_json() or {}

    id_docente = data.get(
        "id_docente"
    )

    if id_docente:
        try:
            docente = db.session.get(
                Usuario,
                int(id_docente),
            )

        except (
            TypeError,
            ValueError
        ):
            docente = None

        if (
            not docente
            or not docente.activo
        ):
            return jsonify({
                "mensaje":
                    "El docente seleccionado no es válido."
            }), 400

        seccion.id_docente = (
            docente.id_usuario
        )

    else:
        seccion.id_docente = None

    try:
        db.session.commit()

        return jsonify({
            "mensaje":
                "Responsable actualizado correctamente.",

            "seccion":
                serializar_seccion(seccion),
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR RESPONSABLE:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible actualizar el responsable."
        }), 500


# =========================================================
# CERRAR CICLO
# =========================================================

@ciclos_bp.post(
    "/<int:id_ciclo>/cerrar"
)
@permission_required("estudiantes.ver")
def cerrar_ciclo(id_ciclo):
    ciclo = db.session.get(
        CicloEscolar,
        id_ciclo,
    )

    if not ciclo:
        return jsonify({
            "mensaje":
                "El ciclo escolar no existe."
        }), 404

    if ciclo.estado == "cerrado":
        return jsonify({
            "mensaje":
                "El ciclo ya está cerrado."
        }), 400

    try:
        ciclo.estado = "cerrado"

        db.session.commit()

        return jsonify({
            "mensaje":
                f"Ciclo {ciclo.anio} cerrado correctamente."
        }), 200

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CERRAR CICLO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible cerrar el ciclo."
        }), 500


# =========================================================
# CREAR NUEVO CICLO
# =========================================================

@ciclos_bp.post("")
@permission_required("estudiantes.ver")
def crear_ciclo():
    data = request.get_json() or {}

    try:
        anio = int(
            data.get("anio")
        )

    except (
        TypeError,
        ValueError
    ):
        return jsonify({
            "mensaje":
                "Ingrese un año escolar válido."
        }), 400

    if anio < 2026 or anio > 2100:
        return jsonify({
            "mensaje":
                "Ingrese un año escolar válido."
        }), 400

    existente = (
        CicloEscolar.query
        .filter_by(
            anio=anio
        )
        .first()
    )

    if existente:
        return jsonify({
            "mensaje":
                "Ya existe un ciclo escolar para ese año."
        }), 400

    try:
        fecha_inicio = date.fromisoformat(
            data.get(
                "fecha_inicio",
                ""
            )
        )

        fecha_fin = date.fromisoformat(
            data.get(
                "fecha_fin",
                ""
            )
        )

    except (
        ValueError,
        TypeError
    ):
        return jsonify({
            "mensaje":
                "Ingrese fechas válidas."
        }), 400

    if fecha_fin <= fecha_inicio:
        return jsonify({
            "mensaje":
                "La fecha final debe ser posterior a la inicial."
        }), 400

    copiar_estructura = bool(
        data.get(
            "copiar_estructura"
        )
    )

    conservar_responsables = bool(
        data.get(
            "conservar_responsables"
        )
    )

    promover_estudiantes = bool(
        data.get(
            "promover_estudiantes"
        )
    )

    if (
        promover_estudiantes
        and not copiar_estructura
    ):
        return jsonify({
            "mensaje":
                "Para promover estudiantes debe copiar la estructura."
        }), 400

    ciclo_actual = obtener_ciclo_base()

    if not ciclo_actual:
        return jsonify({
            "mensaje":
                "No se encontró un ciclo escolar base."
        }), 400

    if anio <= ciclo_actual.anio:
        return jsonify({
            "mensaje":
                "El nuevo ciclo debe ser posterior al ciclo más reciente."
        }), 400

    try:
        secciones_origen = (
            Seccion.query
            .filter_by(
                id_ciclo=
                    ciclo_actual.id_ciclo,

                activo=True,
            )
            .order_by(
                Seccion.grado.asc(),
                Seccion.nombre.asc(),
            )
            .all()
        )

        nuevo_ciclo = CicloEscolar(
            anio=anio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado="activo",
        )

        db.session.add(
            nuevo_ciclo
        )

        db.session.flush()

        nuevas_secciones = {}

        # COPIAR ESTRUCTURA
        if copiar_estructura:
            for origen in secciones_origen:
                nueva = Seccion(
                    id_ciclo=
                        nuevo_ciclo.id_ciclo,

                    grado=
                        origen.grado,

                    nombre=
                        origen.nombre.upper(),

                    id_docente=(
                        origen.id_docente
                        if conservar_responsables
                        else None
                    ),

                    activo=True,
                )

                db.session.add(
                    nueva
                )

                db.session.flush()

                clave = (
                    origen.grado,
                    origen.nombre.upper(),
                )

                nuevas_secciones[
                    clave
                ] = nueva

        promovidos = 0
        egresados = 0
        omitidos = 0
        secciones_creadas = 0

        # PROMOVER ESTUDIANTES
        if promover_estudiantes:
            matriculas = (
                Matricula.query
                .filter_by(
                    id_ciclo=
                        ciclo_actual.id_ciclo
                )
                .filter(
                    Matricula.estado
                    != "Retirada"
                )
                .all()
            )

            for matricula in matriculas:
                seccion_origen = (
                    matricula.seccion
                )

                if not seccion_origen:
                    omitidos += 1
                    continue

                # Sexto ya no se promueve automáticamente.
                if seccion_origen.grado >= 6:
                    egresados += 1
                    continue

                grado_destino = (
                    seccion_origen.grado + 1
                )

                nombre_destino = (
                    seccion_origen.nombre.upper()
                )

                clave_destino = (
                    grado_destino,
                    nombre_destino,
                )

                destino = (
                    nuevas_secciones.get(
                        clave_destino
                    )
                )

                # Si no existe el grado siguiente,
                # se crea automáticamente.
                if not destino:
                    destino = (
                        crear_seccion_promocion(
                            nuevo_ciclo=
                                nuevo_ciclo,

                            grado=
                                grado_destino,

                            nombre=
                                nombre_destino,
                        )
                    )

                    nuevas_secciones[
                        clave_destino
                    ] = destino

                    secciones_creadas += 1

                # Evitar matrícula duplicada.
                ya_matriculado = (
                    Matricula.query
                    .filter_by(
                        id_estudiante=
                            matricula.id_estudiante,

                        id_ciclo=
                            nuevo_ciclo.id_ciclo,
                    )
                    .first()
                )

                if ya_matriculado:
                    omitidos += 1
                    continue

                nueva_matricula = (
                    Matricula(
                        id_estudiante=
                            matricula.id_estudiante,

                        id_ciclo=
                            nuevo_ciclo.id_ciclo,

                        id_seccion=
                            destino.id_seccion,

                        estado=
                            "Activa",
                    )
                )

                db.session.add(
                    nueva_matricula
                )

                promovidos += 1

        ciclo_actual.estado = "cerrado"

        db.session.commit()

        mensaje = (
            f"Ciclo {anio} creado correctamente. "
            f"{promovidos} estudiante"
            f"{'s' if promovidos != 1 else ''} "
            f"promovido"
            f"{'s' if promovidos != 1 else ''}."
        )

        if secciones_creadas:
            mensaje += (
                f" {secciones_creadas} sección"
                f"{'es' if secciones_creadas != 1 else ''} "
                f"creada"
                f"{'s' if secciones_creadas != 1 else ''} "
                f"automáticamente."
            )

        if egresados:
            mensaje += (
                f" {egresados} estudiante"
                f"{'s' if egresados != 1 else ''} "
                f"de sexto terminó primaria."
            )

        if omitidos:
            mensaje += (
                f" {omitidos} registro"
                f"{'s' if omitidos != 1 else ''} "
                f"no pudo promoverse automáticamente."
            )

        return jsonify({
            "mensaje":
                mensaje,

            "id_ciclo":
                nuevo_ciclo.id_ciclo,

            "promovidos":
                promovidos,

            "egresados":
                egresados,

            "omitidos":
                omitidos,

            "secciones_creadas":
                secciones_creadas,
        }), 201

    except Exception as error:
        db.session.rollback()

        print(
            "ERROR CREAR CICLO:",
            repr(error),
        )

        return jsonify({
            "mensaje":
                "No fue posible crear el ciclo escolar."
        }), 500