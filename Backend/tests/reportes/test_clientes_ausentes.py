from datetime import date, time

from src.cliente.models import Cliente
from src.reserva.estados import EstadoReserva
from src.reserva.models import Reserva


URL = "/reportes/clientes-ausentes"


def test_reporte_agrupa_ausencias_y_toma_la_ultima_reserva(cliente, persistir):
    ana = Cliente(
        dni="30111222",
        nombre="Ana",
        apellido="Pérez",
        telefono="1111111111",
    )
    bruno = Cliente(
        dni="30444555",
        nombre="Bruno",
        apellido="Gómez",
        telefono="2222222222",
    )
    ana_id, bruno_id = persistir(ana, bruno)
    persistir(
        Reserva(
            fecha=date(2026, 6, 1),
            hora=time(20, 0),
            cant_comensales=2,
            cliente_id=ana_id,
            estado=EstadoReserva.AUSENTE,
        ),
        Reserva(
            fecha=date(2026, 6, 10),
            hora=time(21, 30),
            cant_comensales=4,
            cliente_id=ana_id,
            estado=EstadoReserva.AUSENTE,
        ),
        Reserva(
            fecha=date(2026, 6, 5),
            hora=time(13, 0),
            cant_comensales=2,
            cliente_id=bruno_id,
            estado=EstadoReserva.AUSENTE,
        ),
    )

    response = cliente.get(URL)

    assert response.status_code == 200
    assert response.json() == {
        "clientes": [
            {
                "dni": "30111222",
                "nombre": "Ana",
                "apellido": "Pérez",
                "ultima_fecha": "2026-06-10",
                "ultima_hora": "21:30:00",
                "cantidad_ausencias": 2,
            },
            {
                "dni": "30444555",
                "nombre": "Bruno",
                "apellido": "Gómez",
                "ultima_fecha": "2026-06-05",
                "ultima_hora": "13:00:00",
                "cantidad_ausencias": 1,
            },
        ]
    }


def test_reporte_solo_incluye_reservas_ausentes(cliente, persistir):
    cliente_db = Cliente(
        dni="30999888",
        nombre="Carla",
        apellido="López",
        telefono="3333333333",
    )
    cliente_id = persistir(cliente_db)
    persistir(
        Reserva(
            fecha=date(2026, 6, 12),
            hora=time(19, 0),
            cant_comensales=2,
            cliente_id=cliente_id,
            estado=EstadoReserva.CON_COMANDA,
        )
    )

    response = cliente.get(URL)

    assert response.status_code == 200
    assert response.json() == {"clientes": []}
