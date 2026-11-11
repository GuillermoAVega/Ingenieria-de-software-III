from calendar import monthrange
from datetime import date, datetime, timedelta

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from src.models import Comanda, DetalleComanda, DetalleFactura, Factura
from src.cliente.models import Cliente
from src.mesa.models import Mesa
from src.mozo.models import Mozo
from src.productos.models import Producto
from src.reserva import models as reserva_models
from src.reserva.estados import EstadoReserva
from src.sector.models import Sector
from src.reportes.schemas import (
    ClienteAusenteItem,
    ClientesAusentesRespuesta,
    ComandasPorMozoItem,
    ComandasPorMozoRespuesta,
    ProductoMasVendidoItem,
    ProductosMasVendidosRespuesta,
    PuntoVentaDia,
    VentasComparativaRespuesta,
    OcupacionPorSectorItem,
    OcupacionPorSectorRespuesta,
)
from collections import Counter
from collections.abc import Iterable

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from src.models import ComprobantePago, Factura
from src.reportes.constants import ANIO_MAX, DIAS_SEMANA, MESES
from src.reportes.schemas import (
    CantidadPorDiaSemana,
    CantidadPorMes,
    CantidadVentasRespuesta,
)


def comandas_por_mozo(
    sesion: Session, desde: date, hasta: date
) -> ComandasPorMozoRespuesta:
    """Cuenta comandas activas por fecha y suma las facturas activas asociadas."""
    facturas_por_comanda = (
        select(
            Factura.comanda_id.label("comanda_id"),
            func.sum(Factura.importe_total).label("importe_ventas"),
        )
        .where(Factura.activo.is_(True))
        .group_by(Factura.comanda_id)
        .subquery()
    )
    filas = sesion.execute(
        select(
            Mozo.id,
            Mozo.nombre,
            func.count(Comanda.id),
            func.coalesce(func.sum(facturas_por_comanda.c.importe_ventas), 0),
        )
        .select_from(Mozo)
        .join(
            Comanda,
            (Comanda.mozo_id == Mozo.id)
            & Comanda.activo.is_(True)
            & Comanda.fecha.between(desde, hasta),
        )
        .outerjoin(
            facturas_por_comanda,
            facturas_por_comanda.c.comanda_id == Comanda.id,
        )
        .group_by(Mozo.id, Mozo.nombre)
        .order_by(
            func.sum(facturas_por_comanda.c.importe_ventas).desc(),
            func.count(Comanda.id).desc(),
            Mozo.nombre,
        )
    ).all()
    return ComandasPorMozoRespuesta(
        desde=desde,
        hasta=hasta,
        por_mozo=[
            ComandasPorMozoItem(
                mozo_id=mozo_id,
                nombre=nombre,
                cantidad_comandas=cantidad_comandas,
                importe_ventas=float(importe_ventas),
            )
            for mozo_id, nombre, cantidad_comandas, importe_ventas in filas
        ],
    )



def productos_mas_vendidos(
    sesion: Session, desde: date, hasta: date, limite: int
) -> ProductosMasVendidosRespuesta:
    """Ranking de productos facturados (líneas y facturas activas) en un período inclusivo."""
    unidades = func.sum(DetalleFactura.cantidad)
    importe = func.sum(DetalleFactura.precio_final)
    filas = sesion.execute(
        select(Producto.id, Producto.nombre, Producto.tipo, unidades, importe)
        .select_from(DetalleFactura)
        .join(Factura, Factura.id == DetalleFactura.factura_id)
        .join(DetalleComanda, DetalleComanda.id == DetalleFactura.detalle_comanda_id)
        .join(Producto, Producto.id == DetalleComanda.producto_id)
        .where(
            DetalleFactura.activo.is_(True),
            Factura.activo.is_(True),
            Factura.fecha_hora_emision >= datetime.combine(desde, datetime.min.time()),
            Factura.fecha_hora_emision
            < datetime.combine(hasta + timedelta(days=1), datetime.min.time()),
        )
        .group_by(Producto.id, Producto.nombre, Producto.tipo)
        .order_by(unidades.desc(), importe.desc(), Producto.nombre)
        .limit(limite)
    ).all()
    return ProductosMasVendidosRespuesta(
        desde=desde,
        hasta=hasta,
        limite=limite,
        productos=[
            ProductoMasVendidoItem(
                producto_id=producto_id,
                nombre=nombre,
                tipo=tipo,
                unidades=int(total_unidades),
                importe=round(float(total_importe or 0), 2),
            )
            for producto_id, nombre, tipo, total_unidades, total_importe in filas
        ],
    )


def _mes_anterior(anio: int, mes: int) -> tuple[int, int]:
    return (anio - 1, 12) if mes == 1 else (anio, mes - 1)


def _siguiente_mes(anio: int, mes: int) -> tuple[int, int]:
    return (anio + 1, 1) if mes == 12 else (anio, mes + 1)


def _ventas_por_dia(sesion: Session, anio: int, mes: int) -> list[PuntoVentaDia]:
    """Ventas de facturas activas por día, con los días sin ventas en cero."""
    _, cantidad_dias = monthrange(anio, mes)
    inicio = datetime(anio, mes, 1)
    anio_siguiente, mes_siguiente = _siguiente_mes(anio, mes)
    fin = datetime(anio_siguiente, mes_siguiente, 1)

    fecha = func.date(Factura.fecha_hora_emision)
    filas = sesion.execute(
        select(fecha, func.sum(Factura.importe_total))
        .where(
            Factura.activo.is_(True),
            Factura.fecha_hora_emision >= inicio,
            Factura.fecha_hora_emision < fin,
        )
        .group_by(fecha)
    ).all()

    importes = {
        int(str(fecha_fila)[-2:]): round(float(importe or 0), 2)
        for fecha_fila, importe in filas
    }
    return [
        PuntoVentaDia(dia=dia, importe=importes.get(dia, 0.0))
        for dia in range(1, cantidad_dias + 1)
    ]


def ventas_comparativa(
    sesion: Session, anio: int, mes: int
) -> VentasComparativaRespuesta:
    anio_anterior, mes_anterior = _mes_anterior(anio, mes)
    return VentasComparativaRespuesta(
        anio=anio,
        mes=mes,
        anio_anterior=anio_anterior,
        mes_anterior=mes_anterior,
        actual=_ventas_por_dia(sesion, anio, mes),
        anterior=_ventas_por_dia(sesion, anio_anterior, mes_anterior),
    )


"""Consultas de reportes de ventas."""


def agrupar_ventas(anio: int, fechas: Iterable[datetime]) -> CantidadVentasRespuesta:
    """Cuenta las fechas por mes y por día de la semana (lunes = 0), completando con ceros."""
    fechas = list(fechas)
    por_mes = Counter(fecha.month for fecha in fechas)
    por_dia = Counter(fecha.weekday() for fecha in fechas)
    return CantidadVentasRespuesta(
        anio=anio,
        por_mes=[CantidadPorMes(mes=m, cantidad=por_mes[m]) for m in range(1, MESES + 1)],
        por_dia_semana=[
            CantidadPorDiaSemana(dia=d, cantidad=por_dia[d]) for d in range(DIAS_SEMANA)
        ],
    )


def cantidad_ventas(sesion: Session, anio: int) -> CantidadVentasRespuesta:
    """Ventas del año: facturas activas con al menos un comprobante activo."""
    consulta = select(Factura.fecha_hora_emision).where(
        Factura.activo.is_(True),
        Factura.fecha_hora_emision >= datetime(anio, 1, 1),
        exists().where(
            ComprobantePago.factura_id == Factura.id,
            ComprobantePago.activo.is_(True),
        ),
    )
    if anio < ANIO_MAX:  # datetime(10000, 1, 1) no existe
        consulta = consulta.where(Factura.fecha_hora_emision < datetime(anio + 1, 1, 1))
    return agrupar_ventas(anio, sesion.scalars(consulta).all())


def clientes_ausentes(sesion: Session) -> ClientesAusentesRespuesta:
    """Lista clientes con reservas ausentes, agrupados por cliente."""
    filas = sesion.execute(
        select(
            Cliente.dni,
            Cliente.nombre,
            Cliente.apellido,
            reserva_models.Reserva.fecha,
            reserva_models.Reserva.hora,
        )
        .join(
            reserva_models.Reserva,
            reserva_models.Reserva.cliente_id == Cliente.id,
        )
        .where(reserva_models.Reserva.estado == EstadoReserva.AUSENTE)
        .order_by(
            reserva_models.Reserva.fecha.desc(),
            reserva_models.Reserva.hora.desc(),
            reserva_models.Reserva.id.desc(),
        )
    ).all()

    agrupados: dict[str, ClienteAusenteItem] = {}
    for dni, nombre, apellido, fecha, hora in filas:
        if dni not in agrupados:
            agrupados[dni] = ClienteAusenteItem(
                dni=dni,
                nombre=nombre,
                apellido=apellido,
                ultima_fecha=fecha,
                ultima_hora=hora,
                cantidad_ausencias=0,
            )
        agrupados[dni].cantidad_ausencias += 1

    return ClientesAusentesRespuesta(clientes=list(agrupados.values()))


def ocupacion_por_sector(
    sesion: Session, desde: date, hasta: date
) -> OcupacionPorSectorRespuesta:
    """Calcula mesas atendidas, comandas y rotación por sector."""
    filas = sesion.execute(
        select(
            Sector.id,
            Sector.nombre,
            func.count(distinct(Comanda.mesa_id)),
            func.count(Comanda.id),
        )
        .select_from(Sector)
        .outerjoin(Mesa, Mesa.sector_id == Sector.id)
        .outerjoin(
            Comanda,
            (Comanda.mesa_id == Mesa.id)
            & Comanda.activo.is_(True)
            & Comanda.fecha.between(desde, hasta),
        )
        .group_by(Sector.id, Sector.nombre)
        .order_by(Sector.nombre)
    ).all()

    por_sector = []
    for sector_id, nombre, mesas_atendidas, cantidad_comandas in filas:
        mesas = int(mesas_atendidas or 0)
        comandas = int(cantidad_comandas or 0)
        por_sector.append(
            OcupacionPorSectorItem(
                sector_id=sector_id,
                sector=nombre,
                mesas_atendidas=mesas,
                cantidad_comandas=comandas,
                rotacion=round(comandas / mesas, 2) if mesas else 0.0,
            )
        )

    return OcupacionPorSectorRespuesta(
        desde=desde,
        hasta=hasta,
        por_sector=por_sector,
    )
