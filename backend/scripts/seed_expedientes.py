from datetime import date

from app import create_app
from app.extensions import db

from app.models import (
    CicloEscolar,
    Estudiante,
    Matricula,
    RequisitoExpediente,
    Seccion,
    Usuario,
)


app = create_app()


with app.app_context():
    # =====================================================
    # CICLO 2026
    # =====================================================

    ciclo = CicloEscolar.query.filter_by(
        anio=2026
    ).first()

    if not ciclo:
        raise RuntimeError(
            "No existe el ciclo 2026."
        )

    # =====================================================
    # DOCENTE ANA
    # =====================================================

    ana = Usuario.query.filter(
        Usuario.correo.in_([
            "docente@sgad.demo",
            "ana@sgad.demo",
        ])
    ).first()

    if not ana:
        raise RuntimeError(
            "No existe la docente Ana."
        )

    # =====================================================
    # SECCIÓN
    # =====================================================

    seccion = Seccion.query.filter_by(
        id_ciclo=ciclo.id_ciclo,
        grado=2,
        nombre="A",
    ).first()

    if not seccion:
        seccion = Seccion(
            id_ciclo=ciclo.id_ciclo,
            grado=2,
            nombre="A",
            id_docente=ana.id_usuario,
            activo=True,
        )

        db.session.add(seccion)
        db.session.flush()

    else:
        seccion.id_docente = (
            ana.id_usuario
        )

        seccion.activo = True

    # =====================================================
    # REQUISITOS DEL PROTOTIPO
    # =====================================================

    requisitos = [
        (
            1,
            "Certificación de nacimiento",
        ),
        (
            2,
            "CUI del encargado",
        ),
        (
            3,
            "Constancia de código personal MINEDUC",
        ),
        (
            4,
            "Tarjeta de salud o vacunación",
        ),
        (
            5,
            "Fotografía reciente",
        ),
        (
            6,
            "Constancia del ciclo anterior",
        ),
    ]

    for orden, nombre in requisitos:
        requisito = (
            RequisitoExpediente.query
            .filter_by(
                nombre=nombre
            )
            .first()
        )

        if not requisito:
            requisito = (
                RequisitoExpediente(
                    nombre=nombre,
                    obligatorio=True,
                    activo=True,
                    orden=orden,
                )
            )

            db.session.add(
                requisito
            )

        else:
            requisito.orden = orden
            requisito.activo = True
            requisito.obligatorio = True

    # =====================================================
    # ESTUDIANTE 1
    # =====================================================

    estudiante1 = (
        Estudiante.query
        .filter_by(
            cui="3001000102001"
        )
        .first()
    )

    if not estudiante1:
        estudiante1 = Estudiante(
            codigo="EORM-2026-001",
            cui="3001000102001",
            nombres="Juan Carlos",
            apellidos="López García",
            fecha_nacimiento=date(
                2018,
                3,
                12,
            ),
            genero="Masculino",
            direccion="Aldea El Pinal",
            encargado="Rosa García",
            parentesco="Madre",
            telefono="55112233",
            activo=True,
        )

        db.session.add(
            estudiante1
        )

        db.session.flush()

    # =====================================================
    # ESTUDIANTE 2
    # =====================================================

    estudiante2 = (
        Estudiante.query
        .filter_by(
            cui="3001000202002"
        )
        .first()
    )

    if not estudiante2:
        estudiante2 = Estudiante(
            codigo="EORM-2026-002",
            cui="3001000202002",
            nombres="María Fernanda",
            apellidos="Pérez Díaz",
            fecha_nacimiento=date(
                2018,
                6,
                21,
            ),
            genero="Femenino",
            direccion="Aldea El Pinal",
            encargado="Ana Díaz",
            parentesco="Madre",
            telefono="55112234",
            activo=True,
        )

        db.session.add(
            estudiante2
        )

        db.session.flush()

    # =====================================================
    # MATRÍCULAS
    # =====================================================

    for estudiante in [
        estudiante1,
        estudiante2,
    ]:
        matricula = (
            Matricula.query
            .filter_by(
                id_estudiante=
                    estudiante.id_estudiante,

                id_ciclo=
                    ciclo.id_ciclo,
            )
            .first()
        )

        if not matricula:
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

    print("")
    print(
        "======================================"
    )
    print(
        " EXPEDIENTES CARGADOS CORRECTAMENTE"
    )
    print(
        "======================================"
    )
    print(
        "Sección: Segundo A"
    )
    print(
        "Docente: Ana"
    )
    print(
        "Estudiantes: 2"
    )
    print(
        "Requisitos: 6"
    )
    print(
        "======================================"
    )