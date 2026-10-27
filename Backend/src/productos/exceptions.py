# Excepciones de dominio en Python puro: no dependen de FastAPI.
# El router las traduce a respuestas HTTP mediante manejadores globales.


class ErrorDominio(Exception):
    """Base de todos los errores de dominio de productos."""
    MENSAJE = "Error de dominio"

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.MENSAJE
        super().__init__(self.mensaje)


class ProductoNoEncontrado(ErrorDominio):
    MENSAJE = "Producto no encontrado"


class ComponenteInvalido(ErrorDominio):
    """Componentes inexistentes o de tipo incorrecto en el campo `campo`."""
    MENSAJE = "Hay componentes inexistentes o de tipo incorrecto"

    def __init__(self, campo: str, ids: list[int], mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.campo = campo
        self.ids = ids


class ErrorConflicto(ErrorDominio):
    """Base de los errores que se responden como conflicto (409)."""
    MENSAJE = "Conflicto con el estado actual del producto"


class NombreDuplicado(ErrorConflicto):
    MENSAJE = "Ya existe un producto activo con ese nombre"


class ComponenteInactivo(ErrorConflicto):
    MENSAJE = "Hay componentes dados de baja"

    def __init__(self, ids: list[int], mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.ids = ids


class BajaRestringida(ErrorConflicto):
    """El producto no puede darse de baja porque otros activos dependen de él."""
    MENSAJE = "El producto es componente de otros productos activos"

    def __init__(self, bloqueantes: list[int], mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.bloqueantes = sorted(bloqueantes)
