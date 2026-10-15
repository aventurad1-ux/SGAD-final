from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token
)

from app.extensions import db
from app.models.usuario import Usuario
from app.models.refresh_token import RefreshToken
from app.services.password_service import verify_password


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    correo = data.get("correo", "").strip().lower()
    password = data.get("password", "")

    if not correo or not password:
        return jsonify({
            "message": "Correo y contraseña son obligatorios."
        }), 400

    usuario = Usuario.query.filter_by(
        correo=correo
    ).first()

    if not usuario:
        return jsonify({
            "message": "Credenciales incorrectas."
        }), 401

    if not usuario.activo:
        return jsonify({
            "message": "La cuenta se encuentra desactivada."
        }), 403

    if not verify_password(
        usuario.contrasena_hash,
        password
    ):
        return jsonify({
            "message": "Credenciales incorrectas."
        }), 401

    claims = {
        "rol": usuario.rol.nombre
    }

    access_token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims=claims
    )

    refresh_token = create_refresh_token(
        identity=str(usuario.id_usuario),
        additional_claims=claims
    )

    refresh_data = decode_token(refresh_token)

    token_db = RefreshToken(
        id_usuario=usuario.id_usuario,
        jti=refresh_data["jti"],
        fecha_expiracion=datetime.fromtimestamp(
            refresh_data["exp"],
            tz=timezone.utc
        ),
        direccion_ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent")
    )

    db.session.add(token_db)
    db.session.commit()

    return jsonify({
        "message": "Inicio de sesión exitoso.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre
        }
    }), 200