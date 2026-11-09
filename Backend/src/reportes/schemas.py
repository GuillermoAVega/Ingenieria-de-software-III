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


class CantidadPorMes(BaseModel):
    mes: int
    cantidad: int


class CantidadPorDiaSemana(BaseModel):
    dia: int  # 0 = lunes
    cantidad: int


class CantidadVentasRespuesta(BaseModel):
    anio: int
    por_mes: list[CantidadPorMes]
    por_dia_semana: list[CantidadPorDiaSemana]
