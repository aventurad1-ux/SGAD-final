import os
import shutil
import subprocess
import tempfile
import zipfile

from datetime import datetime
from pathlib import Path

from flask import current_app


def obtener_pg_dump():
    """
    Busca pg_dump de forma compatible con desarrollo
    local en Windows y despliegue en Linux.
    """

    # 1. Ruta configurada mediante variable de entorno
    ruta_configurada = (
        os.getenv("PG_DUMP_PATH")
        or current_app.config.get("PG_DUMP_PATH")
    )

    if ruta_configurada:
        ruta = Path(ruta_configurada)

        if ruta.is_file():
            return str(ruta)

    # 2. Buscar pg_dump en el PATH del sistema
    ruta_path = shutil.which("pg_dump")

    if ruta_path:
        return ruta_path

    # 3. Rutas comunes en Windows
    rutas_windows = [
        r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
        r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
    ]

    for ruta in rutas_windows:
        if Path(ruta).is_file():
            return ruta

    raise RuntimeError(
        "No se encontró pg_dump. "
        "Configure PG_DUMP_PATH o agregue PostgreSQL al PATH."
    )


def generar_respaldo():
    backend = Path(current_app.root_path).parent

    carpeta_documentos = backend / "storage"

    carpeta_respaldos = backend / "backups"
    carpeta_respaldos.mkdir(
        parents=True,
        exist_ok=True
    )

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    nombre_respaldo = (
        f"respaldo_sgad_{fecha}.zip"
    )

    ruta_respaldo = (
        carpeta_respaldos / nombre_respaldo
    )

    configuracion = current_app.config

    pg_dump = obtener_pg_dump()

    with tempfile.TemporaryDirectory() as temporal:
        archivo_sql = (
            Path(temporal) / "base_datos.sql"
        )

        variables = os.environ.copy()

        variables["PGPASSWORD"] = str(
            configuracion["DB_PASSWORD"]
        )

        comando = [
            pg_dump,
            "-h",
            str(configuracion["DB_HOST"]),
            "-p",
            str(configuracion["DB_PORT"]),
            "-U",
            str(configuracion["DB_USER"]),
            "-d",
            str(configuracion["DB_NAME"]),
            "--no-owner",
            "--no-privileges",
            "-f",
            str(archivo_sql),
        ]

        resultado = subprocess.run(
            comando,
            env=variables,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        if resultado.returncode != 0:
            current_app.logger.error(
                "Error de pg_dump: %s",
                resultado.stderr,
            )

            raise RuntimeError(
                "No se pudo generar el respaldo "
                "de PostgreSQL."
            )

        if not archivo_sql.is_file():
            raise RuntimeError(
                "No se generó el archivo SQL."
            )

        try:
            with zipfile.ZipFile(
                ruta_respaldo,
                "w",
                zipfile.ZIP_DEFLATED,
            ) as archivo_zip:

                archivo_zip.write(
                    archivo_sql,
                    "base_datos.sql",
                )

                if carpeta_documentos.exists():

                    for archivo in (
                        carpeta_documentos.rglob("*")
                    ):
                        if not archivo.is_file():
                            continue

                        if archivo.is_symlink():
                            continue

                        ruta_relativa = (
                            archivo.relative_to(
                                backend
                            )
                        )

                        archivo_zip.write(
                            archivo,
                            str(ruta_relativa),
                        )

        except Exception:
            ruta_respaldo.unlink(
                missing_ok=True
            )
            raise

    if not ruta_respaldo.is_file():
        raise RuntimeError(
            "El archivo de respaldo "
            "no pudo ser creado."
        )

    return {
        "nombre": nombre_respaldo,
        "ruta": str(ruta_respaldo),
        "fecha": datetime.now().isoformat(),
        "tamano": ruta_respaldo.stat().st_size,
        "estado": "completado",
    }