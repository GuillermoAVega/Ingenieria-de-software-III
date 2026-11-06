from datetime import date, time

from src.models import Comanda
from src.mesa.models import Mesa
from src.mozo.models import Mozo
from src.sector.models import Sector


def test_comanda_puede_asociarse_a_varias_mesas(sesion):
    sector = Sector(
        nombre="Salón",
        apto_fumadores=False,
        piso=1,
    )
    mesas = [
        Mesa(capacidad=2, disponible=True, sector=sector),
        Mesa(capacidad=4, disponible=True, sector=sector),
    ]
    mozo = Mozo(nombre="Luis", nro_legajo=10)
    sesion.add_all([sector, *mesas, mozo])
    sesion.flush()
    comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        mozo_id=mozo.id,
        mesa_id=mesas[0].id,
        mesas_asociadas=mesas,
    )
    sesion.add(comanda)
    sesion.commit()
    sesion.refresh(comanda)

    assert comanda.mesa_ids == [mesas[0].id, mesas[1].id]


def test_comanda_de_reserva_puede_no_tener_mozo(sesion):
    sector = Sector(
        nombre="Salón",
        apto_fumadores=False,
        piso=1,
    )
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    sesion.add_all([sector, mesa])
    sesion.flush()

    comanda = Comanda(
        fecha=date(2026, 6, 15),
        hora=time(20, 0),
        mozo_id=None,
        mesa_id=mesa.id,
    )

    sesion.add(comanda)
    sesion.commit()

    assert comanda.mozo_id is None
