from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.usuario import Usuario


def permission_required(permission_code):
    def decorator(function):

        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):

            usuario_id = int(get_jwt_identity())

            usuario = db.session.get(
                Usuario,
                usuario_id
            )

            if not usuario or not usuario.activo:
                return jsonify({
                    "message": "Usuario no disponible."
                }), 401

            permisos_rol = {
                permiso.codigo
                for permiso in usuario.rol.permisos
                if permiso.activo
            }

            permisos_usuario = {}

            for permiso_asignado in usuario.permisos_individuales:
                permisos_usuario[
                    permiso_asignado.permiso.codigo
                ] = permiso_asignado.permitido

            if permission_code in permisos_usuario:
                permitido = permisos_usuario[
                    permission_code
                ]
            else:
                permitido = (
                    permission_code in permisos_rol
                )

            if not permitido:
                return jsonify({
                    "message": "No tiene permiso para realizar esta acción."
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator