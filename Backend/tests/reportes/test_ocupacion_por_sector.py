from datetime import date, time

from src.models import Comanda
from src.mesa.models import Mesa
from src.sector.models import Sector


URL = "/reportes/ocupacion-por-sector"


def test_reporte_calcula_mesas_comandas_y_rotacion_por_sector(cliente, persistir):
    salon = Sector(nombre="Salón", apto_fumadores=False, piso="Planta baja")
    terraza = Sector(nombre="Terraza", apto_fumadores=True, piso="Planta baja")
    salon_id, terraza_id = persistir(salon, terraza)
    mesa_salon_1_id, mesa_salon_2_id, mesa_terraza_id = persistir(
        Mesa(capacidad=2, disponible=True, sector_id=salon_id),
        Mesa(capacidad=4, disponible=True, sector_id=salon_id),
        Mesa(capacidad=4, disponible=True, sector_id=terraza_id),
    )
    persistir(
        Comanda(
            fecha=date(2026, 6, 10), hora=time(12), mesa_id=mesa_salon_1_id, mozo_id=None
        ),
        Comanda(
            fecha=date(2026, 6, 11), hora=time(13), mesa_id=mesa_salon_1_id, mozo_id=None
        ),
        Comanda(
            fecha=date(2026, 6, 12), hora=time(20), mesa_id=mesa_salon_2_id, mozo_id=None
        ),
        Comanda(
            fecha=date(2026, 6, 12), hora=time(20), mesa_id=mesa_terraza_id, mozo_id=None
        ),
    )

    response = cliente.get(URL, params={"desde": "2026-06-01", "hasta": "2026-06-30"})

    assert response.status_code == 200
    assert response.json() == {
        "desde": "2026-06-01",
        "hasta": "2026-06-30",
        "por_sector": [
            {
                "sector_id": salon_id,
                "sector": "Salón",
                "mesas_atendidas": 2,
                "cantidad_comandas": 3,
                "rotacion": 1.5,
            },
            {
                "sector_id": terraza_id,
                "sector": "Terraza",
                "mesas_atendidas": 1,
                "cantidad_comandas": 1,
                "rotacion": 1.0,
            },
        ],
    }


def test_reporte_rechaza_periodo_invertido(cliente):
    response = cliente.get(URL, params={"desde": "2026-06-30", "hasta": "2026-06-01"})

    assert response.status_code == 422
