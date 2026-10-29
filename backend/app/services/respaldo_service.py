import os
import shutil
import subprocess
import tempfile
import zipfile

from datetime import datetime
from pathlib import Path

from flask import current_app


def generar_respaldo():

    # Ubicación de las carpetas del proyecto
    backend = Path(current_app.root_path).parent

    carpeta_documentos = backend / "storage"

    # Los respaldos se guardan fuera de storage
    carpeta_respaldos = backend / "backups"
    carpeta_respaldos.mkdir(
        parents=True,
        exist_ok=True
    )

    # Nombre único para cada respaldo
    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    nombre_respaldo = f"respaldo_sgad_{fecha}.zip"

    ruta_respaldo = carpeta_respaldos / nombre_respaldo

    # Configuración existente de PostgreSQL
    configuracion = current_app.config

    pg_dump = (
        r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
    )

    # Comprobar que existe pg_dump
    if not Path(pg_dump).is_file():
        raise RuntimeError(
            "No se encontró pg_dump de PostgreSQL."
        )

    # Crear carpeta temporal
    with tempfile.TemporaryDirectory() as temporal:

        archivo_sql = Path(temporal) / "base_datos.sql"

        # Contraseña enviada de forma segura al proceso
        variables = os.environ.copy()

        variables["PGPASSWORD"] = configuracion[
            "DB_PASSWORD"
        ]

        # Generar copia de PostgreSQL
        comando = [
            pg_dump,
            "-h", configuracion["DB_HOST"],
            "-p", str(configuracion["DB_PORT"]),
            "-U", configuracion["DB_USER"],
            "-d", configuracion["DB_NAME"],
            "--no-owner",
            "--no-privileges",
            "-f", str(archivo_sql)
        ]

        resultado = subprocess.run(
            comando,
            env=variables,
            capture_output=True,
            text=True,
            timeout=300,
            check=False
        )

        if resultado.returncode != 0:
            raise RuntimeError(
                "No se pudo generar el respaldo "
                "de PostgreSQL."
            )

        if not archivo_sql.is_file():
            raise RuntimeError(
                "No se generó el archivo SQL."
            )

        # Crear el ZIP con la base de datos y documentos
        try:
            with zipfile.ZipFile(
                ruta_respaldo,
                "w",
                zipfile.ZIP_DEFLATED
            ) as archivo_zip:

                archivo_zip.write(
                    archivo_sql,
                    "base_datos.sql"
                )

                if carpeta_documentos.exists():

                    for archivo in carpeta_documentos.rglob("*"):

                        if archivo.is_file():

                            # Evitar incluir enlaces simbólicos
                            if archivo.is_symlink():
                                continue

                            ruta_relativa = archivo.relative_to(
                                backend
                            )

                            archivo_zip.write(
                                archivo,
                                str(ruta_relativa)
                            )

        except Exception:
            ruta_respaldo.unlink(missing_ok=True)
            raise

    return {
        "nombre": nombre_respaldo,
        "ruta": str(ruta_respaldo),
        "fecha": datetime.now().isoformat(),
        "tamano": ruta_respaldo.stat().st_size,
        "estado": "completado"
    }