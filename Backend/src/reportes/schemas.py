from pydantic import BaseModel


class PuntoVentaDia(BaseModel):
    dia: int
    importe: float


class VentasComparativaRespuesta(BaseModel):
    anio: int
    mes: int
    anio_anterior: int
    mes_anterior: int
    actual: list[PuntoVentaDia]
    anterior: list[PuntoVentaDia]
