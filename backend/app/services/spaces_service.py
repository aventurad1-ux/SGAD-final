import os
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)


def _configuracion_spaces():
    access_key = os.getenv(
        "DO_SPACES_ACCESS_KEY"
    )
    secret_key = os.getenv(
        "DO_SPACES_SECRET_KEY"
    )
    region = os.getenv(
        "DO_SPACES_REGION"
    )
    bucket = os.getenv(
        "DO_SPACES_BUCKET"
    )
    endpoint = os.getenv(
        "DO_SPACES_ENDPOINT"
    )

    valores = {
        "access_key": access_key,
        "secret_key": secret_key,
        "region": region,
        "bucket": bucket,
        "endpoint": endpoint,
    }

    faltantes = [
        nombre
        for nombre, valor in valores.items()
        if not valor
    ]

    if faltantes:
        raise RuntimeError(
            "Faltan variables de entorno "
            "para DigitalOcean Spaces: "
            + ", ".join(faltantes)
        )

    return valores


def _cliente_spaces():
    config = _configuracion_spaces()

    cliente = boto3.client(
        "s3",
        region_name=config["region"],
        endpoint_url=config["endpoint"],
        aws_access_key_id=config[
            "access_key"
        ],
        aws_secret_access_key=config[
            "secret_key"
        ],
        config=Config(
            signature_version="s3v4"
        ),
    )

    return cliente, config["bucket"]


def clave_respaldo(nombre_archivo):
    nombre_seguro = Path(
        nombre_archivo
    ).name

    return (
        f"respaldos/{nombre_seguro}"
    )


def subir_respaldo_spaces(
    ruta_archivo
):
    ruta = Path(
        ruta_archivo
    ).resolve()

    if not ruta.is_file():
        raise FileNotFoundError(
            "El archivo de respaldo local "
            "no existe."
        )

    cliente, bucket = (
        _cliente_spaces()
    )

    clave = clave_respaldo(
        ruta.name
    )

    try:
        cliente.upload_file(
            str(ruta),
            bucket,
            clave,
            ExtraArgs={
                "ACL": "private",
                "ContentType":
                    "application/zip",
            },
        )

    except (
        BotoCoreError,
        ClientError,
    ) as error:
        raise RuntimeError(
            "No fue posible subir "
            "el respaldo a "
            "DigitalOcean Spaces."
        ) from error

    return {
        "bucket": bucket,
        "clave": clave,
        "nombre": ruta.name,
    }


def descargar_respaldo_spaces(
    nombre_archivo,
    ruta_destino
):
    destino = Path(
        ruta_destino
    ).resolve()

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cliente, bucket = (
        _cliente_spaces()
    )

    clave = clave_respaldo(
        nombre_archivo
    )

    try:
        cliente.download_file(
            bucket,
            clave,
            str(destino),
        )

    except ClientError as error:
        codigo = (
            error.response
            .get("Error", {})
            .get("Code")
        )

        if codigo in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            raise FileNotFoundError(
                "El respaldo no existe "
                "en DigitalOcean Spaces."
            ) from error

        raise RuntimeError(
            "No fue posible recuperar "
            "el respaldo desde "
            "DigitalOcean Spaces."
        ) from error

    except BotoCoreError as error:
        raise RuntimeError(
            "No fue posible recuperar "
            "el respaldo desde "
            "DigitalOcean Spaces."
        ) from error

    if not destino.is_file():
        raise RuntimeError(
            "Spaces respondió, pero "
            "el archivo no pudo "
            "recuperarse."
        )

    return destino


def respaldo_existe_spaces(
    nombre_archivo
):
    cliente, bucket = (
        _cliente_spaces()
    )

    clave = clave_respaldo(
        nombre_archivo
    )

    try:
        cliente.head_object(
            Bucket=bucket,
            Key=clave,
        )

        return True

    except ClientError as error:
        codigo = (
            error.response
            .get("Error", {})
            .get("Code")
        )

        if codigo in {
            "404",
            "NoSuchKey",
            "NotFound",
        }:
            return False

        raise