from datetime import date, time

import pytest

from src.cliente.models import Cliente
from src.comanda.services import crear_comanda_desde_reserva
from src.comanda.services import obtener_mesas_disponibles
from src.exceptions import BadRequest
from src.detalleReserva.models import DetalleReserva
from src.mesa.models import Mesa
from src.reserva.estados import EstadoReserva
from src.reserva.models import Reserva, ReservaMesa
from src.sector.models import Sector


def test_crear_comanda_desde_reserva_copia_datos_y_detalles(sesion):
    cliente = Cliente(
        dni="12345678",
        nombre="Ana",
        apellido="Pérez",
        telefono="123456",
    )
    sector = Sector(nombre="Salón", apto_fumadores=False, piso=1)
    mesas = [
        Mesa(capacidad=2, disponible=True, sector=sector),
        Mesa(capacidad=4, disponible=True, sector=sector),
    ]
    sesion.add_all([cliente, sector, *mesas])
    sesion.flush()
    reserva = Reserva(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        cant_comensales=5,
        cliente_id=cliente.id,
        mesas_asociadas=[ReservaMesa(mesa_id=mesa.id) for mesa in mesas],
        detalles=[DetalleReserva(producto_id=8, cantidad_producto=2)],
    )
    sesion.add(reserva)
    sesion.commit()

    comanda = crear_comanda_desde_reserva(sesion, reserva.id)

    assert comanda.fecha == reserva.fecha
    assert comanda.hora == reserva.hora
    assert comanda.cliente_id == cliente.id
    assert comanda.mozo_id is None
    assert comanda.mesa_ids == [mesas[0].id, mesas[1].id]
    assert [(d.producto_id, d.cantidad) for d in comanda.detalles] == [(8, 2)]
    assert reserva.estado == EstadoReserva.CON_COMANDA


def test_comanda_inmediata_requiere_mesas_disponibles(sesion):
    sector = Sector(nombre="Salón", apto_fumadores=False, piso=1)
    mesa = Mesa(capacidad=2, disponible=False, sector=sector)
    sesion.add(mesa)
    sesion.flush()

    with pytest.raises(BadRequest, match="no están disponibles"):
        obtener_mesas_disponibles(sesion, [mesa.id])
