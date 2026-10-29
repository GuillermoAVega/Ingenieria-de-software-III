# Excepciones de dominio en Python puro: no dependen de FastAPI ni de productos.
# El router las traduce a respuestas HTTP mediante manejadores globales.


class ErrorSeccion(Exception):
    """Base de todos los errores de dominio de secciones."""
    MENSAJE = "Error de sección"

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.MENSAJE
        super().__init__(self.mensaje)


class SeccionNoEncontrada(ErrorSeccion):
    MENSAJE = "Sección no encontrada"


class NombreSeccionDuplicado(ErrorSeccion):
    MENSAJE = "Ya existe una sección con ese nombre"


class PosicionSeccionDuplicada(ErrorSeccion):
    MENSAJE = "Ya existe una sección en esa posición"
