from datetime import date, time

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from src.cliente.models import Cliente
from src.detalleReserva.models import DetalleReserva
from src.mesa.models import Mesa
from src.models import Comanda, DetalleComanda
from src.reserva.models import Reserva
from src.sector.models import Sector


def _referencias_foraneas(motor, tabla):
    return {
        (fk["constrained_columns"][0], fk["referred_table"])
        for fk in inspect(motor).get_foreign_keys(tabla)
    }


def test_detalle_reserva_referencia_producto(motor):
    assert ("producto_id", "producto") in _referencias_foraneas(
        motor, "detalle_reserva"
    )


def test_detalle_comanda_referencia_producto(motor):
    assert ("producto_id", "producto") in _referencias_foraneas(
        motor, "detalle_comanda"
    )


def test_detalle_reserva_se_navega_desde_el_producto(sesion, crear_postre):
    cliente = Cliente(
        dni="12345678",
        nombre="Ana",
        apellido="Pérez",
        telefono="123456",
    )
    postre = crear_postre()
    sesion.add_all([cliente, postre])
    sesion.flush()

    reserva = Reserva(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        cant_comensales=2,
        cliente_id=cliente.id,
        detalles=[DetalleReserva(producto=postre, cantidad_producto=2)],
    )
    sesion.add(reserva)
    sesion.commit()

    detalle = reserva.detalles[0]
    assert detalle.producto is postre
    assert postre.detalles_reserva == [detalle]


def test_detalle_comanda_se_navega_desde_el_producto(sesion, crear_postre):
    postre = crear_postre()
    sector = Sector(nombre="Salón", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    sesion.add_all([postre, sector, mesa])
    sesion.flush()

    comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        mesa_id=mesa.id,
        detalles=[DetalleComanda(producto=postre, cantidad=2)],
    )
    sesion.add(comanda)
    sesion.commit()

    detalle = comanda.detalles[0]
    assert detalle.producto is postre
    assert postre.detalles_comanda == [detalle]


def test_detalle_reserva_rechaza_producto_inexistente(sesion):
    cliente = Cliente(
        dni="12345678",
        nombre="Ana",
        apellido="Pérez",
        telefono="123456",
    )
    sesion.add(cliente)
    sesion.flush()
    reserva = Reserva(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        cant_comensales=2,
        cliente_id=cliente.id,
    )
    sesion.add(reserva)
    sesion.flush()

    sesion.add(
        DetalleReserva(
            reserva_id=reserva.id,
            producto_id=999,
            cantidad_producto=1,
        )
    )
    with pytest.raises(IntegrityError):
        sesion.commit()


def test_detalle_comanda_rechaza_producto_inexistente(sesion):
    sector = Sector(nombre="Salón", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    sesion.add_all([sector, mesa])
    sesion.flush()

    comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        mesa_id=mesa.id,
        detalles=[DetalleComanda(producto_id=999, cantidad=1)],
    )
    sesion.add(comanda)

    with pytest.raises(IntegrityError):
        sesion.commit()
