# Excepciones exclusivas de los combos, en Python puro (sin FastAPI)
from src.productos.exceptions import ErrorConflicto, ErrorDominio


class FechaHastaVencida(ErrorDominio):
    """La fecha de fin de un combo nuevo ya pasó."""
    MENSAJE = "La fecha de fin no puede ser anterior a hoy"


class ComboVencidoInmutable(ErrorConflicto):
    MENSAJE = "Un combo vencido no puede modificarse"
