from datetime import date, time

from pydantic import BaseModel


class ComandasPorMozoItem(BaseModel):
    mozo_id: int
    nombre: str
    cantidad_comandas: int
    importe_ventas: float


class ComandasPorMozoRespuesta(BaseModel):
    desde: date
    hasta: date
    por_mozo: list[ComandasPorMozoItem]


class ProductoMasVendidoItem(BaseModel):
    producto_id: int
    nombre: str
    tipo: str
    unidades: int
    importe: float


class ProductosMasVendidosRespuesta(BaseModel):
    desde: date
    hasta: date
    limite: int
    productos: list[ProductoMasVendidoItem]


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


class ClienteAusenteItem(BaseModel):
    dni: str
    nombre: str
    apellido: str
    ultima_fecha: date
    ultima_hora: time
    cantidad_ausencias: int


class ClientesAusentesRespuesta(BaseModel):
    clientes: list[ClienteAusenteItem]


class OcupacionPorSectorItem(BaseModel):
    sector_id: int
    sector: str
    mesas_atendidas: int
    cantidad_comandas: int
    rotacion: float


class OcupacionPorSectorRespuesta(BaseModel):
    desde: date
    hasta: date
    por_sector: list[OcupacionPorSectorItem]


class MedioPagoUsoItem(BaseModel):
    medio_pago_id: int
    descripcion: str
    cantidad_comprobantes: int
    importe: float
    importe_promedio: float
    porcentaje_uso: float
    porcentaje_importe: float


class MediosPagoRespuesta(BaseModel):
    desde: date
    hasta: date
    total_comprobantes: int
    total_importe: float
    importe_promedio: float
    medios: list[MedioPagoUsoItem]
