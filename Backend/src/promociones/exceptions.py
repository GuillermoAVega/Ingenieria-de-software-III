# Excepciones de dominio en Python puro: no dependen de FastAPI.
# El router las traduce a respuestas HTTP mediante manejadores globales.


class ErrorPromocion(Exception):
    """Base de todos los errores de dominio de promociones."""
    MENSAJE = "Error de promoción"

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.MENSAJE
        super().__init__(self.mensaje)


class PromocionNoEncontrada(ErrorPromocion):
    MENSAJE = "Promoción no encontrada"


class PromocionEnUso(ErrorPromocion):
    MENSAJE = "La promoción está en uso por líneas de factura y no puede modificarse"


class FechaHastaVencida(ErrorPromocion):
    MENSAJE = "La fecha_hasta no puede ser anterior a hoy"


class ProductosInexistentes(ErrorPromocion):
    """Los ids indicados en `productos_ids` no corresponden a ningún producto."""
    MENSAJE = "Hay productos inexistentes"

    def __init__(self, ids: list[int], mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.ids = sorted(ids)


class ProductosDadosDeBaja(ErrorPromocion):
    MENSAJE = "Hay productos dados de baja"

    def __init__(self, ids: list[int], mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.ids = sorted(ids)
