from src.exceptions import NotFound


def obtener_activo_o_404(db, modelo, id: int):
    """Devuelve el registro activo con ese id o lanza NotFound."""
    obj = db.get(modelo, id)
    if obj is None or not obj.activo:
        raise NotFound()
    return obj
