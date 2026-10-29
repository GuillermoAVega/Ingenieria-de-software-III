from enum import Enum


class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CANCELADA = "cancelada"
    AUSENTE = "ausente"
    CON_COMANDA = "con_comanda"
