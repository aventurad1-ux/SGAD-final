from app import create_app
from app.extensions import db
from app.models import (
    CicloEscolar,
    Matricula,
    Seccion,
)


app = create_app()


with app.app_context():
    ciclo_origen = (
        CicloEscolar.query
        .filter_by(anio=2026)
        .first()
    )

    ciclo_destino = (
        CicloEscolar.query
        .filter_by(anio=2027)
        .first()
    )

    if not ciclo_origen:
        raise RuntimeError(
            "No existe el ciclo 2026."
        )

    if not ciclo_destino:
        raise RuntimeError(
            "No existe el ciclo 2027."
        )

    matriculas = (
        Matricula.query
        .filter_by(
            id_ciclo=ciclo_origen.id_ciclo
        )
        .filter(
            Matricula.estado != "Retirada"
        )
        .all()
    )

    promovidos = 0
    egresados = 0

    for matricula in matriculas:
        seccion_origen = matricula.seccion

        if not seccion_origen:
            continue

        if seccion_origen.grado >= 6:
            egresados += 1
            continue

        existente = (
            Matricula.query
            .filter_by(
                id_estudiante=matricula.id_estudiante,
                id_ciclo=ciclo_destino.id_ciclo,
            )
            .first()
        )

        if existente:
            continue

        grado_destino = (
            seccion_origen.grado + 1
        )

        nombre_destino = (
            seccion_origen.nombre.upper()
        )

        seccion_destino = (
            Seccion.query
            .filter_by(
                id_ciclo=ciclo_destino.id_ciclo,
                grado=grado_destino,
                nombre=nombre_destino,
            )
            .first()
        )

        if not seccion_destino:
            seccion_destino = Seccion(
                id_ciclo=ciclo_destino.id_ciclo,
                grado=grado_destino,
                nombre=nombre_destino,
                id_docente=None,
                activo=True,
            )

            db.session.add(
                seccion_destino
            )

            db.session.flush()

            print(
                f"Sección creada: "
                f"{grado_destino} "
                f"{nombre_destino}"
            )

        nueva_matricula = Matricula(
            id_estudiante=
                matricula.id_estudiante,

            id_ciclo=
                ciclo_destino.id_ciclo,

            id_seccion=
                seccion_destino.id_seccion,

            estado=
                "Activa",
        )

        db.session.add(
            nueva_matricula
        )

        promovidos += 1

    db.session.commit()

    print(
        "Promoción reparada correctamente."
    )

    print(
        f"Promovidos: {promovidos}"
    )

    print(
        f"Egresados de sexto: {egresados}"
    )