import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.backend.database import Base, create_db_engine, create_session_factory, get_session
from app.backend.routes.clientes import router

VALID_PAYLOAD = {
    "dni": "30111222",
    "first_name": "Juan",
    "last_name": "Perez",
    "email": "juan@dominio.com",
    "phone": "11-4444-5555",
}

OTHER_PAYLOAD = {
    "dni": "41234567",
    "first_name": "Ana",
    "last_name": "Lopez",
    "email": "ana@dominio.com",
    "phone": "11-2222-3333",
}


@pytest.fixture
def client():
    engine = create_db_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    def override_get_session():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client


def test_alta_exitosa_crea_cliente_y_devuelve_mensaje(client):
    response = client.post("/clientes", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Cliente registrado exitosamente"
    assert body["customer"]["status"] == "Activo"


def test_campos_obligatorios_vacios_devuelve_las_cinco_advertencias(client):
    payload = {"dni": "", "first_name": "", "last_name": "", "email": "", "phone": ""}

    response = client.post("/clientes", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"dni", "first_name", "last_name", "email", "phone"}


def test_multiples_errores_de_formato_combinados_en_un_intento(client):
    payload = dict(VALID_PAYLOAD)
    payload["first_name"] = "Juan123"
    payload["phone"] = "11-abcd"

    response = client.post("/clientes", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"first_name", "phone"}


def test_dni_con_formato_invalido_devuelve_mensaje_especifico(client):
    payload = dict(VALID_PAYLOAD, dni="123")

    response = client.post("/clientes", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "dni", "message": "El DNI debe contener solo números (7 u 8 dígitos)"}
    ]


def test_telefono_con_formato_invalido_devuelve_mensaje_especifico(client):
    payload = dict(VALID_PAYLOAD, phone="11-abcd")

    response = client.post("/clientes", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "phone", "message": "El teléfono debe contener solo números y guiones"}
    ]


def test_alta_cliente_con_email_sin_tld_es_valido(client):
    payload = dict(VALID_PAYLOAD, email="juan@localhost")

    response = client.post("/clientes", json=payload)

    assert response.status_code == 201


def test_dni_duplicado_endpoint_bloquea_el_alta(client):
    client.post("/clientes", json=VALID_PAYLOAD)

    response = client.post("/clientes", json=VALID_PAYLOAD)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "dni", "message": "El cliente ya se encuentra registrado"}
    ]


def test_alta_con_dni_de_cliente_inactivo_se_permite(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.patch(f"/clientes/{VALID_PAYLOAD['dni']}/baja")

    nuevo_payload = dict(VALID_PAYLOAD, first_name="Ana", last_name="Diaz")
    response = client.post("/clientes", json=nuevo_payload)

    assert response.status_code == 201
    assert response.json()["customer"]["status"] == "Activo"

    listado = client.get("/clientes").json()["customers"]
    con_ese_dni = [c for c in listado if c["dni"] == int(VALID_PAYLOAD["dni"])]
    assert len(con_ese_dni) == 2
    por_estado = {c["status"]: c for c in con_ese_dni}
    assert por_estado["Activo"]["first_name"] == "Ana"
    assert por_estado["Inactivo"]["first_name"] == VALID_PAYLOAD["first_name"]


def test_buscar_cliente_activo_devuelve_sus_datos(client):
    client.post("/clientes", json=VALID_PAYLOAD)

    response = client.get("/clientes/30111222")

    assert response.status_code == 200
    assert response.json()["customer"]["status"] == "Activo"


def test_buscar_cliente_por_dni_con_ceros_a_la_izquierda_lo_encuentra(client):
    client.post("/clientes", json=VALID_PAYLOAD)

    response = client.get("/clientes/030111222")

    assert response.status_code == 200
    assert response.json()["customer"]["dni"] == 30111222


def test_buscar_cliente_inactivo_informa_su_estado(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.patch("/clientes/30111222/baja")

    response = client.get("/clientes/30111222")

    assert response.status_code == 200
    assert response.json()["customer"]["status"] == "Inactivo"


def test_buscar_cliente_inexistente_devuelve_404(client):
    response = client.get("/clientes/30111222")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "dni", "message": "Cliente no encontrado"}
    ]


def test_buscar_cliente_con_formato_invalido_devuelve_404(client):
    response = client.get("/clientes/30.111.222")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "dni", "message": "Cliente no encontrado"}
    ]


def test_baja_cliente_activo_devuelve_mensaje_de_exito(client):
    client.post("/clientes", json=VALID_PAYLOAD)

    response = client.patch("/clientes/30111222/baja")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Cliente dado de baja exitosamente"
    assert body["customer"]["status"] == "Inactivo"

    assert body["customer"]["first_name"] == VALID_PAYLOAD["first_name"]
    assert body["customer"]["last_name"] == VALID_PAYLOAD["last_name"]
    assert body["customer"]["email"] == VALID_PAYLOAD["email"]
    assert body["customer"]["phone"] == VALID_PAYLOAD["phone"]

    posterior = client.get("/clientes/30111222")
    assert posterior.json()["customer"] == body["customer"]


def test_baja_cliente_inexistente_devuelve_404(client):
    response = client.patch("/clientes/30111222/baja")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "dni", "message": "Cliente no encontrado"}
    ]


def test_baja_directa_sobre_cliente_ya_inactivo_no_falla(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.patch("/clientes/30111222/baja")

    response = client.patch("/clientes/30111222/baja")

    assert response.status_code == 200
    assert response.json()["message"] == "Cliente dado de baja exitosamente"
    assert response.json()["customer"]["status"] == "Inactivo"


def test_editar_cliente_activo_guarda_los_cambios(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    edicion = dict(VALID_PAYLOAD, first_name="Juan Ignacio", phone="11-9999-8888")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Cliente modificado exitosamente"
    assert body["customer"]["first_name"] == "Juan Ignacio"
    assert body["customer"]["phone"] == "11-9999-8888"
    assert body["customer"]["status"] == "Activo"


def test_editar_cliente_inactivo_bloquea_la_modificacion(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.patch("/clientes/30111222/baja")
    edicion = dict(VALID_PAYLOAD, first_name="Juan Ignacio")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {
            "field": "status",
            "message": "El cliente está inactivo y no puede modificarse",
        }
    ]

    posterior = client.get("/clientes/30111222")
    assert posterior.json()["customer"]["first_name"] == VALID_PAYLOAD["first_name"]
    assert posterior.json()["customer"]["status"] == "Inactivo"


def test_editar_cliente_sin_cambiar_dni_no_dispara_duplicado(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    edicion = dict(VALID_PAYLOAD, first_name="Juan Ignacio")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 200


def test_editar_cliente_inexistente_devuelve_404(client):
    response = client.put("/clientes/30111222/editar", json=VALID_PAYLOAD)

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "dni", "message": "Cliente no encontrado"}
    ]


def test_editar_cliente_con_campos_invalidos_no_guarda_nada(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    edicion = dict(VALID_PAYLOAD, first_name="Juan123", phone="11-abcd")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"first_name", "phone"}

    posterior = client.get("/clientes/30111222")
    assert posterior.json()["customer"]["first_name"] == VALID_PAYLOAD["first_name"]
    assert posterior.json()["customer"]["phone"] == VALID_PAYLOAD["phone"]


def test_editar_cliente_con_dni_invalido_devuelve_mensaje_especifico(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    edicion = dict(VALID_PAYLOAD, dni="123")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "dni", "message": "El DNI debe contener solo números (7 u 8 dígitos)"}
    ]


def test_editar_cliente_con_email_sin_tld_es_valido(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    edicion = dict(VALID_PAYLOAD, email="juan@localhost")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 200


def test_editar_dni_que_pertenece_a_otro_activo_bloquea_el_intento(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)
    edicion = dict(VALID_PAYLOAD, dni=OTHER_PAYLOAD["dni"], first_name="Juan Ignacio")

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "dni", "message": "El DNI ya está en uso"}
    ]

    posterior = client.get("/clientes/30111222")
    assert posterior.json()["customer"]["first_name"] == VALID_PAYLOAD["first_name"]


def test_editar_dni_que_pertenece_a_otro_inactivo_se_permite(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)
    client.patch(f"/clientes/{OTHER_PAYLOAD['dni']}/baja")
    edicion = dict(VALID_PAYLOAD, dni=OTHER_PAYLOAD["dni"])

    response = client.put("/clientes/30111222/editar", json=edicion)

    assert response.status_code == 200
    assert response.json()["customer"]["dni"] == int(OTHER_PAYLOAD["dni"])
    assert response.json()["customer"]["status"] == "Activo"


def test_buscar_cliente_con_dni_compartido_devuelve_el_activo(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)
    client.patch(f"/clientes/{OTHER_PAYLOAD['dni']}/baja")
    edicion = dict(VALID_PAYLOAD, dni=OTHER_PAYLOAD["dni"])
    client.put("/clientes/30111222/editar", json=edicion)

    response = client.get(f"/clientes/{OTHER_PAYLOAD['dni']}")

    assert response.status_code == 200
    assert response.json()["customer"]["status"] == "Activo"
    assert response.json()["customer"]["first_name"] == VALID_PAYLOAD["first_name"]


def test_listar_clientes_sin_filtro_devuelve_todos(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)
    client.patch(f"/clientes/{OTHER_PAYLOAD['dni']}/baja")

    response = client.get("/clientes")

    assert response.status_code == 200
    body = response.json()
    assert {c["dni"] for c in body["customers"]} == {
        int(VALID_PAYLOAD["dni"]),
        int(OTHER_PAYLOAD["dni"]),
    }
    assert body["page"] == 1
    assert body["has_next"] is False


def test_listar_clientes_con_filtro_insensible_a_tildes(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)

    response = client.get("/clientes", params={"q": "PEREZ", "field": "last_name"})

    assert response.status_code == 200
    body = response.json()
    assert [c["dni"] for c in body["customers"]] == [int(VALID_PAYLOAD["dni"])]


def test_listar_clientes_con_field_first_name_no_matchea_por_apellido(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)

    response = client.get("/clientes", params={"q": "perez", "field": "first_name"})

    assert response.status_code == 200
    assert response.json()["customers"] == []


def test_listar_clientes_con_field_dni_filtra_solo_por_dni(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)

    response = client.get("/clientes", params={"q": "301112", "field": "dni"})

    assert response.status_code == 200
    body = response.json()
    assert [c["dni"] for c in body["customers"]] == [int(VALID_PAYLOAD["dni"])]


def test_listar_clientes_sin_field_usa_first_name_por_defecto(client):
    client.post("/clientes", json=VALID_PAYLOAD)
    client.post("/clientes", json=OTHER_PAYLOAD)

    response = client.get("/clientes", params={"q": "perez"})

    assert response.status_code == 200
    assert response.json()["customers"] == []


def test_listar_clientes_sin_coincidencias_devuelve_lista_vacia(client):
    client.post("/clientes", json=VALID_PAYLOAD)

    response = client.get("/clientes", params={"q": "gomez"})

    assert response.status_code == 200
    assert response.json()["customers"] == []


def test_listar_clientes_pagina_2_devuelve_el_resto(client):
    for i in range(25):
        response = client.post(
            "/clientes",
            json={
                "dni": str(30000000 + i),
                "first_name": "Cliente",
                "last_name": "Apellido",
                "email": f"cliente{i}@dominio.com",
                "phone": "11-4444-5555",
            },
        )
        assert response.status_code == 201

    response = client.get("/clientes", params={"page": 2})

    assert response.status_code == 200
    body = response.json()
    assert len(body["customers"]) == 5
    assert body["page"] == 2
    assert body["has_next"] is False
