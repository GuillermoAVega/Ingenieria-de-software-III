from datetime import date, time

from sqlalchemy import inspect

from src.cliente.models import Cliente
from src.mesa.models import Mesa
from src.models import Comanda
from src.mozo.models import Mozo
from src.reserva.models import Reserva
from src.sector.models import Sector


def _referencias_foraneas(motor, tabla):
    return {
        (fk["constrained_columns"][0], fk["referred_table"])
        for fk in inspect(motor).get_foreign_keys(tabla)
    }


def test_comanda_referencia_mozo_mesa_y_reserva(motor):
    referencias = _referencias_foraneas(motor, "comanda")

    assert ("mozo_id", "mozos") in referencias
    assert ("mesa_id", "mesas") in referencias
    assert ("reserva_id", "reservas") in referencias


def test_relaciones_existentes_con_comanda_se_mantienen(motor):
    assert ("comanda_id", "comanda") in _referencias_foraneas(motor, "factura")
    assert ("comanda_id", "comanda") in _referencias_foraneas(
        motor, "detalle_comanda"
    )


def test_comanda_y_mozo_se_relacionan(sesion):
    sector = Sector(nombre="Salón", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    mozo = Mozo(nombre="Luis", nro_legajo=10)
    sesion.add_all([sector, mesa, mozo])
    sesion.flush()

    comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        mozo_id=mozo.id,
        mesa_id=mesa.id,
    )
    sesion.add(comanda)
    sesion.commit()

    assert comanda.mozo is mozo
    assert mozo.comandas == [comanda]


def test_comanda_y_reserva_se_relacionan(sesion):
    cliente = Cliente(
        dni="12345678",
        nombre="Ana",
        apellido="Pérez",
        telefono="123456",
    )
    sector = Sector(nombre="Salón", apto_fumadores=False, piso="Planta baja")
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    sesion.add_all([cliente, sector, mesa])
    sesion.flush()

    reserva = Reserva(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        cant_comensales=2,
        cliente_id=cliente.id,
    )
    sesion.add(reserva)
    sesion.flush()
    comanda = Comanda(
        fecha=reserva.fecha,
        hora=reserva.hora,
        mesa_id=mesa.id,
        reserva_id=reserva.id,
    )
    sesion.add(comanda)
    sesion.commit()

    assert comanda.reserva is reserva
    assert reserva.comanda is comanda


def test_comanda_y_mesa_se_relacionan(sesion):
    sector = Sector(nombre="Salón", apto_fumadores=False, piso="Planta baja")
    mesas = [
        Mesa(capacidad=2, disponible=True, sector=sector),
        Mesa(capacidad=4, disponible=True, sector=sector),
    ]
    sesion.add_all([sector, *mesas])
    sesion.flush()

    comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        mesa_id=mesas[0].id,
        mesas_asociadas=mesas,
    )
    sesion.add(comanda)
    sesion.commit()

    assert comanda.mesa is mesas[0]
    assert mesas[0].comandas == [comanda]
    assert set(comanda.mesas_asociadas) == set(mesas)
    assert mesas[0].comandas_asociadas == [comanda]
    assert mesas[1].comandas_asociadas == [comanda]
    assert mesas[1].comandas == []
