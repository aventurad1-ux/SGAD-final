from flask import Flask

from config.config import Config
from app.extensions import db, migrate, cors


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "http://localhost:5173"
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
            "message": "Backend SGAD funcionando"
        }

    @app.get("/api/db-test")
    def db_test():
        try:
            with db.engine.connect():
                return {
                    "status": "ok",
                    "message": "Conexion con PostgreSQL exitosa"
                }
        except Exception as error:
            return {
                "status": "error",
                "message": str(error)
            }, 500

    return app