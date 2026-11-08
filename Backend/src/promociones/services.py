# Lógica de negocio de promociones. No importa FastAPI.
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import and_, exists, or_, select, update
from sqlalchemy.orm import Session

from src.models import DetalleComanda, DetalleFactura, Factura
from src.productos import registro  # noqa: F401  (carga los mappers de todos los subtipos)
from src.productos.models import Producto
from src.promociones.exceptions import (
    FechaHastaVencida,
    ProductosDadosDeBaja,
    ProductosInexistentes,
    PromocionEnUso,
    PromocionNoEncontrada,
)
from src.promociones.models import Promocion, promocion_producto
from src.promociones.schemas import PromocionActualizar, PromocionCrear
from src.utils import a_decimal

CENTAVOS = Decimal("0.01")


def promocion_en_uso(sesion: Session, promocion_id: int) -> bool:
    """True si algún `DetalleFactura` (activo o no) referencia la promoción."""
    consulta = select(exists().where(DetalleFactura.promocion_id == promocion_id))
    return bool(sesion.scalar(consulta))


def dar_de_baja_vencidas(sesion: Session, hoy: date) -> None:
    """Baja lógica de toda promoción con `fecha_hasta < hoy`, en una única sentencia."""
    sesion.execute(
        update(Promocion)
        .where(Promocion.fecha_hasta < hoy, Promocion.dado_de_baja.is_(False))
        .values(dado_de_baja=True)
        .execution_options(synchronize_session=False)
    )
    sesion.commit()


def calcular_precio_final(
    precio_unitario: Decimal, cantidad: int, descuento: Decimal | None = None
) -> Decimal:
    """precio_unitario * cantidad * (1 - descuento / 100), a 2 decimales half-up."""
    descuento = Decimal(descuento or 0)
    bruto = Decimal(precio_unitario) * cantidad * (Decimal(100) - descuento) / Decimal(100)
    return bruto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---- Motor agrupado por producto -------------------------------------------


@dataclass(frozen=True)
class LineaGrupo:
    id: int
    precio_unitario: Decimal
    cantidad: int


@dataclass(frozen=True)
class Candidata:
    id: int
    tipo: str
    descuento: Decimal | None
    lleva: int | None
    paga: int | None


@dataclass(frozen=True)
class Asignacion:
    promocion_id: int | None
    precio_final: Decimal
    unidades_gratis: int


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def _bruto(linea: LineaGrupo) -> Decimal:
    return linea.precio_unitario * linea.cantidad


def _gratis_por_linea(lineas: list[LineaGrupo], candidata: Candidata) -> dict[int, int]:
    """Unidades gratis de `lleva_paga` asignadas a las líneas más baratas (empate: menor id)."""
    total = sum(linea.cantidad for linea in lineas)
    restantes = (total // candidata.lleva) * (candidata.lleva - candidata.paga)
    gratis = {}
    for linea in sorted(lineas, key=lambda l: (l.precio_unitario, l.id)):
        asignadas = min(linea.cantidad, restantes)
        gratis[linea.id] = asignadas
        restantes -= asignadas
    return gratis


def _evaluar(lineas: list[LineaGrupo], candidata: Candidata) -> tuple[Decimal, dict[int, Asignacion]]:
    """Ahorro en pesos de la candidata y el resultado por línea si ganara."""
    if candidata.tipo == "porcentaje":
        resultado = {
            l.id: Asignacion(
                candidata.id,
                calcular_precio_final(l.precio_unitario, l.cantidad, candidata.descuento),
                0,
            )
            for l in lineas
        }
        ahorro = sum((_bruto(l) - resultado[l.id].precio_final for l in lineas), Decimal(0))
        return ahorro, resultado
    gratis = _gratis_por_linea(lineas, candidata)
    resultado = {
        l.id: Asignacion(
            candidata.id if gratis[l.id] else None,
            _redondear(l.precio_unitario * (l.cantidad - gratis[l.id])),
            gratis[l.id],
        )
        for l in lineas
    }
    ahorro = sum((l.precio_unitario * gratis[l.id] for l in lineas), Decimal(0))
    return ahorro, resultado


def calcular_grupo(
    lineas: list[LineaGrupo], candidatas: list[Candidata]
) -> dict[int, Asignacion]:
    """Función pura: gana la candidata de mayor ahorro en pesos (empate: menor id; ahorro 0 no gana)."""
    mejor_ahorro, mejor = Decimal(0), None
    for candidata in sorted(candidatas, key=lambda c: c.id):
        ahorro, resultado = _evaluar(lineas, candidata)
        if ahorro > mejor_ahorro:
            mejor_ahorro, mejor = ahorro, resultado
    if mejor is not None:
        return mejor
    return {l.id: Asignacion(None, _redondear(_bruto(l)), 0) for l in lineas}


def recalcular_producto(sesion: Session, factura: Factura, producto_id: int) -> None:
    """Recalcula las líneas activas de `factura` del producto: promoción ganadora, precio y gratis."""
    detalles = list(
        sesion.scalars(
            select(DetalleFactura)
            .join(DetalleComanda, DetalleFactura.detalle_comanda_id == DetalleComanda.id)
            .where(
                DetalleFactura.factura_id == factura.id,
                DetalleFactura.activo.is_(True),
                DetalleComanda.producto_id == producto_id,
            )
            .order_by(DetalleFactura.id)
        )
    )
    if not detalles:
        return
    fecha = factura.fecha_hora_emision.date()
    conservadas = {d.promocion_id for d in detalles if d.promocion_id is not None}
    del_producto = select(promocion_producto.c.promocion_id).where(
        promocion_producto.c.producto_id == producto_id
    )
    promociones = sesion.scalars(
        select(Promocion).where(
            or_(
                and_(
                    Promocion.dado_de_baja.is_(False),
                    Promocion.fecha_desde <= fecha,
                    Promocion.fecha_hasta >= fecha,
                    Promocion.id.in_(del_producto),
                ),
                Promocion.id.in_(conservadas),
            )
        )
    )
    candidatas = [
        Candidata(
            p.id, p.tipo, None if p.descuento is None else a_decimal(p.descuento), p.lleva, p.paga
        )
        for p in promociones
    ]
    lineas = [LineaGrupo(d.id, a_decimal(d.precio_unitario), d.cantidad) for d in detalles]
    asignaciones = calcular_grupo(lineas, candidatas)
    for detalle in detalles:
        asignacion = asignaciones[detalle.id]
        detalle.promocion_id = asignacion.promocion_id
        detalle.precio_final = float(asignacion.precio_final)
        detalle.unidades_gratis = asignacion.unidades_gratis


def marcar_en_uso(sesion: Session, promociones: list[Promocion]) -> list[Promocion]:
    """Fija `en_uso` en cada promoción con una sola consulta agrupada (sin N+1)."""
    ids = [p.id for p in promociones]
    usadas = set()
    if ids:
        usadas = set(
            sesion.scalars(
                select(DetalleFactura.promocion_id)
                .where(DetalleFactura.promocion_id.in_(ids))
                .distinct()
            )
        )
    for promocion in promociones:
        promocion.en_uso = promocion.id in usadas
    return promociones


def listar_promociones(
    sesion: Session, hoy: date, incluir_bajas: bool = False
) -> list[Promocion]:
    """Devuelve las promociones ordenadas por id; las bajas solo si se piden."""
    dar_de_baja_vencidas(sesion, hoy)
    consulta = select(Promocion).order_by(Promocion.id)
    if not incluir_bajas:
        consulta = consulta.where(Promocion.dado_de_baja.is_(False))
    return marcar_en_uso(sesion, list(sesion.scalars(consulta)))


def obtener_promocion(sesion: Session, promocion_id: int) -> Promocion:
    """Devuelve la promoción (activa o dada de baja) o lanza 404, sin dejar la transacción abierta."""
    promocion = sesion.get(Promocion, promocion_id)
    if promocion is None:
        sesion.rollback()
        raise PromocionNoEncontrada()
    return promocion


def _resolver_productos(sesion: Session, ids: list[int]) -> list[Producto]:
    """Carga los productos: inexistentes (422) antes que dados de baja (409)."""
    productos = {p.id: p for p in sesion.scalars(select(Producto).where(Producto.id.in_(ids)))}
    inexistentes = [i for i in ids if i not in productos]
    if inexistentes:
        sesion.rollback()
        raise ProductosInexistentes(inexistentes)
    dados_de_baja = [i for i in ids if productos[i].dado_de_baja]
    if dados_de_baja:
        sesion.rollback()
        raise ProductosDadosDeBaja(dados_de_baja)
    return [productos[i] for i in ids]


def _verificar_fecha_hasta(sesion: Session, fecha_hasta: date, hoy: date) -> None:
    if fecha_hasta < hoy:
        sesion.rollback()
        raise FechaHastaVencida()


def crear_promocion(sesion: Session, datos: PromocionCrear, hoy: date) -> Promocion:
    """Alta atómica. Orden: fecha_hasta vencida (422), productos inexistentes (422), dados de baja (409)."""
    _verificar_fecha_hasta(sesion, datos.fecha_hasta, hoy)
    productos = _resolver_productos(sesion, datos.productos_ids)
    promocion = Promocion(
        nombre=datos.nombre,
        tipo=datos.tipo,
        lleva=datos.lleva,
        paga=datos.paga,
        fecha_desde=datos.fecha_desde,
        fecha_hasta=datos.fecha_hasta,
        descuento=datos.descuento,
        productos=productos,
    )
    sesion.add(promocion)
    sesion.commit()
    return promocion


def actualizar_promocion(
    sesion: Session, promocion_id: int, datos: PromocionActualizar, hoy: date
) -> Promocion:
    """Reemplazo completo. Orden: 404, en uso (409), fecha_hasta si cambia (422), productos nuevos (422/409)."""
    promocion = obtener_promocion(sesion, promocion_id)
    if promocion_en_uso(sesion, promocion_id):
        sesion.rollback()
        raise PromocionEnUso()
    if datos.fecha_hasta != promocion.fecha_hasta:
        _verificar_fecha_hasta(sesion, datos.fecha_hasta, hoy)

    conservados = {p.id: p for p in promocion.productos}
    ids_nuevos = [i for i in datos.productos_ids if i not in conservados]
    nuevos = _resolver_productos(sesion, ids_nuevos) if ids_nuevos else []
    por_id = {**conservados, **{p.id: p for p in nuevos}}

    promocion.nombre = datos.nombre
    promocion.tipo = datos.tipo
    promocion.lleva = datos.lleva
    promocion.paga = datos.paga
    promocion.fecha_desde = datos.fecha_desde
    promocion.fecha_hasta = datos.fecha_hasta
    promocion.descuento = datos.descuento
    promocion.productos = [por_id[i] for i in datos.productos_ids]
    sesion.commit()
    return promocion


def dar_de_baja_promocion(sesion: Session, promocion_id: int) -> None:
    """Baja lógica idempotente; se permite aunque la promoción esté en uso."""
    promocion = obtener_promocion(sesion, promocion_id)
    promocion.dado_de_baja = True
    sesion.commit()
