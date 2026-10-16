import os

from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-desarrollo")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "sgad")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "jwt-desarrollo-cambiar-despues"
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)