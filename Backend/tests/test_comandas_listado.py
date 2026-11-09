from datetime import date, time

from src.models import Comanda
from src.mesa.models import Mesa
from src.sector.models import Sector


def test_listar_comandas_prioriza_las_mas_recientes(cliente, sesion):
    sector = Sector(nombre="Salón", apto_fumadores=False, piso=1)
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    sesion.add_all([sector, mesa])
    sesion.flush()

    comandas = [
        Comanda(fecha=date(2026, 6, 14), hora=time(23), mesa_id=mesa.id),
        Comanda(fecha=date(2026, 6, 15), hora=time(19), mesa_id=mesa.id),
        Comanda(fecha=date(2026, 6, 15), hora=time(21), mesa_id=mesa.id),
    ]
    sesion.add_all(comandas)
    sesion.commit()
    ids_esperados = [comandas[2].id, comandas[1].id]
    sesion.close()

    respuesta = cliente.get("/comandas?limit=2")

    assert respuesta.status_code == 200
    assert [comanda["id"] for comanda in respuesta.json()] == ids_esperados
