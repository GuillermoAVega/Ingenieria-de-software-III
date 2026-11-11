from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.cliente.models import Cliente
from src.exceptions import BadRequest, NotFound
from src.mesa.models import Mesa
from src.atencion.models import Atencion
from src.models import Comanda, DetalleComanda, Factura
from src.models.comanda import comanda_mesas as comanda_mesas_tabla
from src.mozo.models import Mozo
from src.reserva.estados import EstadoReserva
from src.reserva.models import Reserva
from src.utils import exigir_producto_activo

MINUTOS_ANTES_COMANDA_RESERVA = 15
MINUTOS_DESPUES_COMANDA_RESERVA = 30


def ocupar_mesas(mesas: list[Mesa]) -> None:
    for mesa in mesas:
        mesa.disponible = False


def liberar_mesas(mesas: list[Mesa]) -> None:
    for mesa in mesas:
        mesa.disponible = True


def obtener_mesas_disponibles(
    db: Session,
    mesa_ids: list[int],
) -> list[Mesa]:
    mesas = db.scalars(
        select(Mesa).where(
            Mesa.id.in_(mesa_ids),
            Mesa.estado.is_(True),
            Mesa.disponible.is_(True),
        )
    ).all()
    if len(mesas) != len(set(mesa_ids)):
        raise BadRequest(detail="Una o más mesas no están disponibles")
    return mesas


def _atenciones_vigentes(db: Session, sector_id: int) -> list[Atencion]:
    hoy = date.today()
    return db.scalars(
        select(Atencion)
        .where(
            Atencion.sector_id == sector_id,
            Atencion.estado.is_(True),
            Atencion.fecha_desde <= hoy,
            (Atencion.fecha_hasta.is_(None) | (Atencion.fecha_hasta >= hoy)),
        )
        .order_by(Atencion.id)
    ).all()


def _sector_unico(mesas: list[Mesa]) -> int:
    sector_ids = {mesa.sector_id for mesa in mesas}
    if len(sector_ids) != 1:
        raise BadRequest(
            detail="Las mesas de una comanda deben pertenecer al mismo sector"
        )
    return next(iter(sector_ids))


def asignar_mozo_para_mesas(db: Session, mesas: list[Mesa]) -> int:
    atenciones = _atenciones_vigentes(db, _sector_unico(mesas))
    if not atenciones:
        raise BadRequest(detail="No hay un mozo asignado al sector de la mesa")

    mozo_ids = [atencion.mozo_id for atencion in atenciones]
    comandas_abiertas = db.scalars(
        select(Comanda).where(
            Comanda.mozo_id.in_(mozo_ids),
            Comanda.activo.is_(True),
            Comanda.estado == "abierta",
        )
    ).all()
    tareas_por_mozo = {mozo_id: 0 for mozo_id in mozo_ids}
    for comanda in comandas_abiertas:
        tareas_por_mozo[comanda.mozo_id] += 1

    return min(mozo_ids, key=lambda mozo_id: (tareas_por_mozo[mozo_id], mozo_id))


def crear_comanda_desde_reserva(
    db: Session,
    reserva_id: int,
) -> Comanda:
    reserva = db.scalar(select(Reserva).where(Reserva.id == reserva_id))
    if reserva is None:
        raise NotFound(detail="La reserva no existe")
    if reserva.estado != EstadoReserva.PENDIENTE:
        raise BadRequest(detail="La reserva no está pendiente")

    ahora = datetime.now()
    fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora)
    desde = fecha_hora_reserva - timedelta(minutes=MINUTOS_ANTES_COMANDA_RESERVA)
    hasta = fecha_hora_reserva + timedelta(minutes=MINUTOS_DESPUES_COMANDA_RESERVA)
    if ahora < desde or ahora > hasta:
        raise BadRequest(
            detail="La comanda solo puede crearse desde 15 minutos antes hasta 30 minutos despues de la reserva"
        )

    existente = db.scalar(
        select(Comanda).where(
            Comanda.reserva_id == reserva_id,
            Comanda.activo.is_(True),
        )
    )
    if existente is not None:
        raise BadRequest(detail="La reserva ya tiene una comanda")
    if not reserva.mesa_ids:
        raise BadRequest(detail="La reserva no tiene mesas asignadas")
    mesas = db.scalars(
        select(Mesa).where(Mesa.id.in_(reserva.mesa_ids))
    ).all()

    comanda = Comanda(
        fecha=reserva.fecha,
        hora=reserva.hora,
        mozo_id=None,
        mesa_id=reserva.mesa_ids[0],
        cliente_id=reserva.cliente_id,
        reserva_id=reserva.id,
        mesas_asociadas=mesas,
        detalles=[
            DetalleComanda(
                producto_id=detalle.producto_id,
                cantidad=detalle.cantidad_producto,
            )
            for detalle in reserva.detalles
        ],
    )
    ocupar_mesas(mesas)
    db.add(comanda)
    reserva.estado = EstadoReserva.CON_COMANDA
    db.commit()
    db.refresh(comanda)
    return comanda


def _validar_cliente(db: Session, cliente_id: int) -> None:
    cliente = db.get(Cliente, cliente_id)
    if cliente is None or not cliente.estado:
        raise BadRequest(detail="El cliente no existe o está dado de baja")


def _validar_mozo(db: Session, mozo_id: int, sector_id: int) -> None:
    mozo = db.get(Mozo, mozo_id)
    if mozo is None or not mozo.estado:
        raise BadRequest(detail="El mozo no existe o está dado de baja")
    if mozo_id not in {a.mozo_id for a in _atenciones_vigentes(db, sector_id)}:
        raise BadRequest(detail="El mozo no atiende el sector de las mesas de la comanda")


def _validar_reserva(db: Session, reserva_id: int, comanda_id: int) -> None:
    if db.get(Reserva, reserva_id) is None:
        raise BadRequest(detail="La reserva no existe")
    otra = db.scalar(
        select(Comanda).where(
            Comanda.reserva_id == reserva_id,
            Comanda.activo.is_(True),
            Comanda.id != comanda_id,
        )
    )
    if otra is not None:
        raise BadRequest(detail="La reserva ya tiene una comanda")


def _mesas_actuales(comanda: Comanda) -> list[Mesa]:
    mesas = list(comanda.mesas_asociadas)
    if comanda.mesa is not None and comanda.mesa not in mesas:
        mesas.append(comanda.mesa)
    return mesas


def _reasignar_mesas(db: Session, comanda: Comanda, nuevas_ids: list[int]) -> None:
    """Cambia las mesas dejando mesa_id, comanda_mesas y disponible coherentes."""
    nuevas_ids = list(dict.fromkeys(nuevas_ids))
    actuales = _mesas_actuales(comanda)
    ids_actuales = {mesa.id for mesa in actuales}
    mesas = db.scalars(
        select(Mesa).where(Mesa.id.in_(nuevas_ids), Mesa.estado.is_(True))
    ).all()
    if len(mesas) != len(nuevas_ids):
        raise BadRequest(detail="Una o más mesas no existen o están dadas de baja")
    if any(mesa.id not in ids_actuales and not mesa.disponible for mesa in mesas):
        raise BadRequest(detail="Una o más mesas no están disponibles")
    _sector_unico(mesas)
    por_id = {mesa.id: mesa for mesa in mesas}
    ordenadas = [por_id[i] for i in nuevas_ids]
    liberar_mesas([mesa for mesa in actuales if mesa.id not in por_id])
    ocupar_mesas(ordenadas)
    comanda.mesas_asociadas = ordenadas
    comanda.mesa_id = nuevas_ids[0]


def crear_comanda(db: Session, datos) -> Comanda:
    if datos.reserva_id is not None:
        return crear_comanda_desde_reserva(db, datos.reserva_id)
    mesa_ids = datos.mesa_ids or ([datos.mesa_id] if datos.mesa_id is not None else [])
    mesa_ids = list(dict.fromkeys(mesa_ids))
    if not mesa_ids:
        raise BadRequest(detail="Debe indicar al menos una mesa")
    if datos.cliente_id is not None:
        _validar_cliente(db, datos.cliente_id)
    for detalle in datos.detalles:
        exigir_producto_activo(db, detalle.producto_id)
    mesas = obtener_mesas_disponibles(db, mesa_ids)
    if datos.comensales is not None and sum(m.capacidad for m in mesas) < datos.comensales:
        raise BadRequest(
            detail="La capacidad de las mesas seleccionadas no alcanza para todos los comensales"
        )
    ahora = datetime.now()
    mozo_id = asignar_mozo_para_mesas(db, mesas)
    ocupar_mesas(mesas)
    comanda = Comanda(
        fecha=datos.fecha or ahora.date(),
        hora=datos.hora or ahora.time().replace(microsecond=0),
        mozo_id=mozo_id,
        mesa_id=mesa_ids[0],
        cliente_id=datos.cliente_id,
        mesas_asociadas=mesas,
        detalles=[DetalleComanda(**d.model_dump()) for d in datos.detalles],
    )
    db.add(comanda)
    db.commit()
    db.refresh(comanda)
    return comanda


def modificar_comanda(db: Session, comanda: Comanda, cambios: dict) -> Comanda:
    if cambios.get("estado", "") is None:
        del cambios["estado"]
    nuevo_estado = cambios.get("estado")
    if comanda.estado == "cerrada" and set(cambios) - {"estado"}:
        raise BadRequest(detail="La comanda está cerrada: reabrila antes de modificarla")
    if nuevo_estado == "cerrada":
        activos = [d for d in comanda.detalles if d.activo]
        if not activos:
            raise BadRequest(detail="No se puede cerrar una comanda sin productos")
        if any(not d.entregado for d in activos):
            raise BadRequest(detail="No se puede cerrar la comanda: hay productos pendientes de entrega")
    if nuevo_estado == "abierta" and comanda.factura and comanda.factura.activo:
        raise BadRequest(detail="La comanda ya fue facturada")

    mesa_ids = cambios.pop("mesa_ids", None)
    mesa_id = cambios.pop("mesa_id", None)
    if mesa_ids is None and mesa_id is not None and mesa_id != comanda.mesa_id:
        mesa_ids = [mesa_id]
    if cambios.get("cliente_id") is not None:
        _validar_cliente(db, cambios["cliente_id"])
    if cambios.get("reserva_id") is not None:
        _validar_reserva(db, cambios["reserva_id"], comanda.id)

    mesas_cambian = mesa_ids is not None and set(mesa_ids) != {
        m.id for m in _mesas_actuales(comanda)
    }
    if mesas_cambian:
        _reasignar_mesas(db, comanda, mesa_ids)
    mozo_id = cambios.get("mozo_id")
    if mozo_id is not None:
        _validar_mozo(db, mozo_id, _sector_unico(_mesas_actuales(comanda)))
    elif mesas_cambian and "mozo_id" not in cambios and comanda.mozo_id is not None:
        sector_id = _sector_unico(_mesas_actuales(comanda))
        if comanda.mozo_id not in {a.mozo_id for a in _atenciones_vigentes(db, sector_id)}:
            comanda.mozo_id = asignar_mozo_para_mesas(db, _mesas_actuales(comanda))

    for campo, valor in cambios.items():
        setattr(comanda, campo, valor)
    db.commit()
    db.refresh(comanda)
    return comanda


def eliminar_comanda(db: Session, comanda: Comanda) -> None:
    factura = db.scalars(
        select(Factura).where(Factura.comanda_id == comanda.id, Factura.activo)
    ).first()
    if factura:
        raise BadRequest(detail="No se puede eliminar una comanda con factura activa")
    if comanda.estado == "abierta":  # al facturar ya se liberaron las mesas
        for mesa in _mesas_actuales(comanda):
            otra_abierta = db.scalar(
                select(Comanda.id)
                .outerjoin(comanda_mesas_tabla, comanda_mesas_tabla.c.comanda_id == Comanda.id)
                .where(
                    Comanda.id != comanda.id,
                    Comanda.activo.is_(True),
                    Comanda.estado == "abierta",
                    (Comanda.mesa_id == mesa.id) | (comanda_mesas_tabla.c.mesa_id == mesa.id),
                )
                .limit(1)
            )
            if otra_abierta is None:
                mesa.disponible = True
    reserva = comanda.reserva
    if reserva is not None and reserva.estado == EstadoReserva.CON_COMANDA:
        reserva.estado = EstadoReserva.PENDIENTE
    comanda.activo = False
    for detalle in comanda.detalles:
        detalle.activo = False
    db.commit()
