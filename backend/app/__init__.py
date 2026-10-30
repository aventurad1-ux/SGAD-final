import os
from datetime import datetime, timezone

from app.models.refresh_token import RefreshToken
from app.services.sesion_service import sesion_vigente
from flask import Flask
from app.services.limites_acceso import limiter

from config.config import Config
from app.extensions import (
    db,
    migrate,
    cors,
    jwt,
)

from app.routes.review_inbox import (
    review_inbox_bp,
)

from app.routes.requests import (
    requests_bp,
)

from app.routes.expedientes import (
    expedientes_bp,
)

from app.routes.ciclos import (
    ciclos_bp,
)

from app.routes.usuarios import (
    usuarios_bp,
)

from app.routes.docente_estudiantes import (
    docente_estudiantes_bp,
)

from app.routes.docente_solicitudes import (
    docente_solicitudes_bp,
)

from app.routes.docente_documentos import (
    docente_documentos_bp,
)

from app.routes.docente_perfil import (
    docente_perfil_bp,
)

from app.routes.repositorio import (
    repositorio_bp,
)

from app.routes.papelera import (
    papelera_bp
)

from app.routes.notificaciones import (
    notificaciones_bp,
)

from app.routes.perfil_directora import (
    perfil_directora_bp,
)

# NUEVO: Módulo de respaldos
from app.routes.respaldos import (
    respaldos_bp,
)

from app.routes.bitacora import (
    bitacora_bp,
)

from app.routes.seguridad_2fa import seguridad_2fa_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object(
        Config
    )
    limiter.init_app(app)

    db.init_app(app)

    migrate.init_app(
        app,
        db,
    )

    jwt.init_app(app)
    @jwt.token_in_blocklist_loader
    def verificar_sesion_jwt(jwt_header, jwt_payload):
        # Rechazamos tokens anteriores a la
        # implementación obligatoria del 2FA.
        if jwt_payload.get("mfa") is not True:
            return True

        tipo = jwt_payload.get("type")

        if tipo == "refresh":
            id_sesion = jwt_payload.get("jti")
        elif tipo == "access":
            id_sesion = jwt_payload.get("sid")
        else:
            return True

        if not id_sesion:
            return True

        sesion = RefreshToken.query.filter_by(
            jti=id_sesion
        ).first()

        if not sesion_vigente(sesion):
            return True

        if str(sesion.id_usuario) != str(
            jwt_payload.get("sub")
        ):
            return True

        # Una solicitud autenticada válida
        # actualiza la última actividad.
        sesion.ultima_actividad = datetime.now(
            timezone.utc
        )
        db.session.commit()

        return False


    from app import models

    origenes_permitidos = [
        origen.strip()
        for origen in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origen.strip()
    ]

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": origenes_permitidos
            }
        }
    )

    @app.get("/")
    def index():
        return {
            "name": "SGAD API",
            "status": "running"
        }

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "message":
                "Backend SGAD funcionando"
        }

    @app.get("/api/db-test")
    def db_test():
        try:
            with db.engine.connect():
                return {
                    "status": "ok",
                    "message":
                        "Conexion con PostgreSQL exitosa"
                }

        except Exception as error:
            return {
                "status": "error",
                "message": str(error)
            }, 500

    from app.routes.auth import (
        auth_bp,
    )

    from app.routes.test_permissions import (
        test_permissions_bp,
    )

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        test_permissions_bp
    )

    app.register_blueprint(
        review_inbox_bp
    )

    app.register_blueprint(
        requests_bp
    )

    app.register_blueprint(
        expedientes_bp
    )

    app.register_blueprint(
        ciclos_bp
    )

    app.register_blueprint(
        usuarios_bp
    )

    app.register_blueprint(
        docente_estudiantes_bp
    )

    app.register_blueprint(
        docente_solicitudes_bp
    )

    app.register_blueprint(
        docente_documentos_bp
    )

    app.register_blueprint(
        docente_perfil_bp
    )

    app.register_blueprint(
        repositorio_bp
     )

    app.register_blueprint(
        papelera_bp
    )

    app.register_blueprint(
        notificaciones_bp
    )

    app.register_blueprint(
        perfil_directora_bp
    )
    # NUEVO: Registrar las rutas de respaldos
    app.register_blueprint(
        respaldos_bp
    )

    app.register_blueprint(
        bitacora_bp
    )

    app.register_blueprint(seguridad_2fa_bp)

    return app