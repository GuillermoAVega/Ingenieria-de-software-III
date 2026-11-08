from decimal import Decimal

from src.exceptions import NotFound, ProductoDadoDeBaja, ProductoInexistente


def obtener_activo_o_404(db, modelo, id: int):
    """Devuelve el registro activo con ese id o lanza NotFound."""
    obj = db.get(modelo, id)
    if obj is None or not obj.activo:
        raise NotFound()
    return obj


def exigir_producto_activo(db, producto_id: int):
    """Devuelve el producto o lanza 422 si no existe / 409 si está dado de baja."""
    from src.productos import registro  # noqa: F401  (carga los mappers de los subtipos)
    from src.productos.models import Producto

    producto = db.get(Producto, producto_id)
    if producto is None:
        raise ProductoInexistente(producto_id)
    if producto.dado_de_baja:
        raise ProductoDadoDeBaja()
    return producto


def a_decimal(valor) -> Decimal:
    """Convierte vía `str` para no arrastrar el error binario de los float."""
    return Decimal(str(valor))
