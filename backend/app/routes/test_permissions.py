from flask import Blueprint, jsonify

from app.utils.permissions import permission_required


test_permissions_bp = Blueprint(
    "test_permissions",
    __name__,
    url_prefix="/api/test"
)


@test_permissions_bp.get("/usuarios")
@permission_required("usuarios.ver")
def ver_usuarios():
    return jsonify({
        "message": "Tiene permiso para ver usuarios."
    }), 200