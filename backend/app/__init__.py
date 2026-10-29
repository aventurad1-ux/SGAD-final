from flask import Flask

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

from app.routes.perfil_directora import (
    perfil_directora_bp,
)


def create_app():
    app = Flask(__name__)

    app.config.from_object(
        Config
    )

    db.init_app(app)
    migrate.init_app(
        app,
        db,
    )
    jwt.init_app(app)

    from app import models

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins":
                    "http://localhost:5173"
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
        perfil_directora_bp
    )
    return app