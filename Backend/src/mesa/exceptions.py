from src.exceptions import BadRequest, NotFound


class SectorMesaNoEncontrado(NotFound):
    DETAIL = "El sector indicado no existe"


class SectorMesaInactivo(BadRequest):
    DETAIL = "No se puede asociar la mesa a un sector inactivo"