from pydantic import BaseModel


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
