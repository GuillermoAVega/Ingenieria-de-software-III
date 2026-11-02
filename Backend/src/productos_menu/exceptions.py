# Excepciones de dominio en Python puro: no dependen de FastAPI ni de productos.
# El router las traduce a respuestas HTTP mediante manejadores globales.


class ErrorProductoMenu(Exception):
    """Base de todos los errores de dominio del menú del día."""
    MENSAJE = "Error de menú del día"

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.MENSAJE
        super().__init__(self.mensaje)


class ProductoInexistente(ErrorProductoMenu):
    """El `producto_id` indicado no corresponde a ningún producto."""
    MENSAJE = "El producto indicado no existe"

    def __init__(self, producto_id: int, mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.producto_id = producto_id


class ProductoDadoDeBaja(ErrorProductoMenu):
    MENSAJE = "El producto está dado de baja"


class FechaMenuOcupada(ErrorProductoMenu):
    MENSAJE = "Ya existe un menú del día en esa fecha"


class ProductoMenuNoEncontrado(ErrorProductoMenu):
    MENSAJE = "Menú del día no encontrado"
