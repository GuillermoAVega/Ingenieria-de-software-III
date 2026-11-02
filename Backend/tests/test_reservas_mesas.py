import pytest

from src.cliente.models import Cliente
from src.mesa.models import Mesa
from src.sector.models import Sector


@pytest.fixture
def reserva_datos(persistir):
    cliente = Cliente(
        dni="12345678",
        nombre="Ada",
        apellido="Lovelace",
        telefono="123456",
    )
    sector = Sector(
        nombre="Salón",
        apto_fumadores=False,
        piso="Planta baja",
    )
    mesa_pequena = Mesa(capacidad=2, disponible=True, sector=sector)
    mesa_grande = Mesa(capacidad=3, disponible=True, sector=sector)
    cliente_id, _, mesa_pequena_id, mesa_grande_id = persistir(
        cliente,
        sector,
        mesa_pequena,
        mesa_grande,
    )
    return {
        "cliente_id": cliente_id,
        "mesa_pequena_id": mesa_pequena_id,
        "mesa_grande_id": mesa_grande_id,
    }


def _payload(cliente_id, mesa_ids, cant_comensales=3):
    return {
        "fecha": "2099-01-01",
        "hora": "20:00",
        "cant_comensales": cant_comensales,
        "observaciones": None,
        "cliente_id": cliente_id,
        "mesa_ids": mesa_ids,
        "detalles": [],
    }


def test_crear_reserva_requiere_mesa_y_capacidad_suficiente(cliente, reserva_datos):
    datos = reserva_datos
    sin_mesas = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], []),
    )
    capacidad_insuficiente = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [datos["mesa_pequena_id"]]),
    )

    assert sin_mesas.status_code == 422
    assert capacidad_insuficiente.status_code == 422
    assert "capacidad total" in capacidad_insuficiente.json()["detail"]


def test_modificar_reserva_valida_mesas_y_capacidad(cliente, reserva_datos):
    datos = reserva_datos
    creada = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [datos["mesa_grande_id"]]),
    )
    reserva_id = creada.json()["id"]
    cuerpo_actualizacion = {
        **_payload(datos["cliente_id"], [datos["mesa_pequena_id"]], 3),
        "estado": "pendiente",
    }

    sin_mesas = cliente.put(
        f"/reservas/{reserva_id}",
        json={**cuerpo_actualizacion, "mesa_ids": []},
    )
    capacidad_insuficiente = cliente.put(
        f"/reservas/{reserva_id}",
        json=cuerpo_actualizacion,
    )

    assert creada.status_code == 201
    assert sin_mesas.status_code == 422
    assert capacidad_insuficiente.status_code == 422
    assert cliente.get(f"/reservas/{reserva_id}").json()["mesa_ids"] == [
        datos["mesa_grande_id"]
    ]

    modificada = cliente.put(
        f"/reservas/{reserva_id}",
        json={
            **cuerpo_actualizacion,
            "mesa_ids": [datos["mesa_pequena_id"], datos["mesa_grande_id"]],
        },
    )
    assert modificada.status_code == 200
    assert set(modificada.json()["mesa_ids"]) == {
        datos["mesa_pequena_id"],
        datos["mesa_grande_id"],
    }


def test_no_se_puede_quitar_mesa_si_rompe_la_capacidad(cliente, reserva_datos):
    datos = reserva_datos
    creada = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [datos["mesa_grande_id"]]),
    )
    reserva_id = creada.json()["id"]

    respuesta = cliente.delete(
        f"/reservas/{reserva_id}/mesas/{datos['mesa_grande_id']}"
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"/reservas/{reserva_id}").json()["mesa_ids"] == [
        datos["mesa_grande_id"]
    ]


def test_no_se_puede_reservar_la_misma_mesa_en_la_misma_fecha_y_hora(
    cliente,
    reserva_datos,
):
    datos = reserva_datos
    mesa_id = datos["mesa_grande_id"]
    primera = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [mesa_id]),
    )
    segunda = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [mesa_id]),
    )

    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert f"La mesa {mesa_id} ya está reservada" in segunda.json()["detail"]


def test_modificar_reserva_no_permite_ocupar_una_mesa_ya_reservada(
    cliente,
    reserva_datos,
):
    datos = reserva_datos
    mesa_id = datos["mesa_grande_id"]
    existente = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [mesa_id]),
    )
    a_modificar = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [datos["mesa_pequena_id"]], 2),
    )

    respuesta = cliente.put(
        f"/reservas/{a_modificar.json()['id']}",
        json={
            **_payload(datos["cliente_id"], [mesa_id]),
            "estado": "pendiente",
        },
    )

    assert existente.status_code == 201
    assert a_modificar.status_code == 201
    assert respuesta.status_code == 409
    assert cliente.get(f"/reservas/{a_modificar.json()['id']}").json()["mesa_ids"] == [
        datos["mesa_pequena_id"]
    ]


def test_una_mesa_puede_reservarse_en_otro_horario(cliente, reserva_datos):
    datos = reserva_datos
    mesa_id = datos["mesa_grande_id"]
    primera = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [mesa_id]),
    )
    otro_horario = _payload(datos["cliente_id"], [mesa_id])
    otro_horario["hora"] = "21:00"

    segunda = cliente.post("/reservas", json=otro_horario)

    assert primera.status_code == 201
    assert segunda.status_code == 201


def test_agregar_mesa_no_permite_una_reserva_existente(cliente, reserva_datos):
    datos = reserva_datos
    existente = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [datos["mesa_grande_id"]]),
    )
    a_modificar = cliente.post(
        "/reservas",
        json=_payload(datos["cliente_id"], [datos["mesa_pequena_id"]], 2),
    )

    respuesta = cliente.post(
        f"/reservas/{a_modificar.json()['id']}/mesas",
        json={"mesa_id": datos["mesa_grande_id"]},
    )

    assert existente.status_code == 201
    assert a_modificar.status_code == 201
    assert respuesta.status_code == 409
