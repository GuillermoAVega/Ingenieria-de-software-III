# Excepciones de dominio en Python puro: no dependen de FastAPI ni de productos.
# El router las traduce a respuestas HTTP mediante manejadores globales.


class ErrorProductoMenu(Exception):
    """Base de todos los errores de dominio del menú del día."""
    MENSAJE = "Error de menú del día"

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.MENSAJE
        super().__init__(self.mensaje)


class MenuDelDiaInexistente(ErrorProductoMenu):
    """El `menu_del_dia_id` indicado no corresponde a ningún producto."""
    MENSAJE = "El menú del día indicado no existe"

    def __init__(self, menu_del_dia_id: int, mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.menu_del_dia_id = menu_del_dia_id


class ProductoNoMenuDelDia(ErrorProductoMenu):
    """El producto existe pero no es un MenuDelDia: solo ese subtipo puede asignarse a una fecha."""
    MENSAJE = "El producto indicado no es un menú del día"

    def __init__(self, menu_del_dia_id: int, mensaje: str | None = None) -> None:
        super().__init__(mensaje)
        self.menu_del_dia_id = menu_del_dia_id


class MenuDelDiaDadoDeBaja(ErrorProductoMenu):
    MENSAJE = "El menú del día está dado de baja"


class FechaMenuPasada(ErrorProductoMenu):
    """La fecha del menú del día es anterior a hoy."""
    MENSAJE = "La fecha del menú del día no puede ser anterior a hoy"


class FechaMenuOcupada(ErrorProductoMenu):
    MENSAJE = "Ya existe un menú del día en esa fecha"


class ProductoMenuNoEncontrado(ErrorProductoMenu):
    MENSAJE = "Menú del día no encontrado"
