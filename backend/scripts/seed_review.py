from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.services.password_service import hash_password

from app.models import (
    CicloEscolar,
    Solicitud,
    SolicitudDestinatario,
    SolicitudRequisito,
    Entrega,
    VersionEntrega,
    Usuario,
    Role,
)


app = create_app()


with app.app_context():
    # -------------------------------------------------
    # DIRECTORA
    # -------------------------------------------------

    directora = Usuario.query.filter_by(
        correo="directora@sgad.demo"
    ).first()

    if not directora:
        raise RuntimeError(
            "No existe la usuaria directora@sgad.demo"
        )

    # -------------------------------------------------
    # ROL DOCENTE REAL
    # -------------------------------------------------

    rol_docente = Role.query.filter_by(
        nombre="Docente"
    ).first()

    if not rol_docente:
        rol_docente = Role(
            nombre="Docente",
            descripcion="Docente del establecimiento",
            activo=True,
        )

        db.session.add(rol_docente)
        db.session.flush()

    # -------------------------------------------------
    # CICLO 2026
    # -------------------------------------------------

    ciclo = CicloEscolar.query.filter_by(
        anio=2026
    ).first()

    if not ciclo:
        ciclo = CicloEscolar(
            anio=2026,
            fecha_inicio=datetime(
                2026, 1, 15
            ).date(),
            fecha_fin=datetime(
                2026, 10, 31
            ).date(),
            estado="activo",
        )

        db.session.add(ciclo)
        db.session.flush()

    # -------------------------------------------------
    # DOCENTE DEMO
    # -------------------------------------------------

    docente = Usuario.query.filter_by(
        correo="docente@sgad.demo"
    ).first()

    if not docente:
        docente = Usuario(
            id_rol=rol_docente.id_rol,
            nombres="Ana",
            apellidos="López",
            correo="docente@sgad.demo",
            contrasena_hash=hash_password(
                "Docente2026"
            ),
            activo=True,
        )

        db.session.add(docente)
        db.session.flush()

    else:
        # Corrige el usuario que habíamos creado
        # temporalmente con rol de Directora.
        docente.id_rol = rol_docente.id_rol

    # -------------------------------------------------
    # SOLICITUD DE PRUEBA
    # -------------------------------------------------

    solicitud = Solicitud.query.filter_by(
        titulo="Planificación de Unidad IV"
    ).first()

    if not solicitud:
        solicitud = Solicitud(
            titulo="Planificación de Unidad IV",
            descripcion=(
                "Entrega de la planificación "
                "correspondiente a la Unidad IV."
            ),
            id_usuario_creador=
                directora.id_usuario,
            id_ciclo=ciclo.id_ciclo,
            fecha_publicacion=datetime(
                2026,
                10,
                15,
                8,
                0,
                tzinfo=timezone.utc,
            ),
            fecha_limite=datetime(
                2026,
                10,
                20,
                23,
                59,
                tzinfo=timezone.utc,
            ),
            prioridad="normal",
            estado="publicada",
        )

        db.session.add(solicitud)
        db.session.flush()

    # -------------------------------------------------
    # DESTINATARIO
    # -------------------------------------------------

    destinatario = (
        SolicitudDestinatario.query
        .filter_by(
            id_solicitud=
                solicitud.id_solicitud,
            id_docente=
                docente.id_usuario,
        )
        .first()
    )

    if not destinatario:
        destinatario = SolicitudDestinatario(
            id_solicitud=
                solicitud.id_solicitud,
            id_docente=
                docente.id_usuario,
            estado="entregado",
        )

        db.session.add(destinatario)
        db.session.flush()

    # -------------------------------------------------
    # REQUISITO
    # -------------------------------------------------

    requisito = (
        SolicitudRequisito.query
        .filter_by(
            id_solicitud=
                solicitud.id_solicitud,
            nombre_documento=
                "Planificación de Unidad IV",
        )
        .first()
    )

    if not requisito:
        requisito = SolicitudRequisito(
            id_solicitud=
                solicitud.id_solicitud,
            nombre_documento=
                "Planificación de Unidad IV",
            descripcion=
                "Documento en formato PDF.",
            obligatorio=True,
            formato_permitido=
                "application/pdf",
            orden=1,
            activo=True,
        )

        db.session.add(requisito)
        db.session.flush()

    # -------------------------------------------------
    # ENTREGA
    # -------------------------------------------------

    entrega = Entrega.query.filter_by(
        id_destinatario=
            destinatario.id_destinatario,
        id_requisito_solicitud=
            requisito.id_requisito_solicitud,
    ).first()

    if not entrega:
        entrega = Entrega(
            id_destinatario=
                destinatario.id_destinatario,
            id_requisito_solicitud=
                requisito.id_requisito_solicitud,
            estado="entregado",
            fecha_primera_entrega=
                datetime.now(timezone.utc),
        )

        db.session.add(entrega)
        db.session.flush()

    # -------------------------------------------------
    # VERSIÓN
    # -------------------------------------------------

    version = VersionEntrega.query.filter_by(
        id_entrega=entrega.id_entrega,
        numero_version=1,
    ).first()

    if not version:
        version = VersionEntrega(
            id_entrega=entrega.id_entrega,
            numero_version=1,
            nombre_archivo=
                "planificacion_unidad_IV.pdf",
            ruta_archivo=
                "demo/planificacion_unidad_IV.pdf",
            tipo_mime="application/pdf",
            tamano_bytes=245760,
            hash_archivo="a" * 64,
            comentario="Primera entrega.",
            id_usuario=docente.id_usuario,
        )

        db.session.add(version)

    db.session.commit()

    print(
        "Datos de prueba actualizados correctamente."
    )