
from app.extensions import db
from app.models.bitacora import Bitacora


def registrar_actividad(
    id_usuario,
    accion,
    modulo,
    descripcion=None
):
    """
    Prepara un registro de actividad en la bitácora.

    El registro se guarda definitivamente cuando
    la operación que lo llamó confirma la transacción
    con db.session.commit().
    """

    registro = Bitacora(
        id_usuario=id_usuario,
        accion=accion,
        modulo=modulo,
        descripcion=descripcion
    )

    db.session.add(registro)

    return registro
