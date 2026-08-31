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


def test_dni_duplicado_endpoint_bloquea_el_alta(client):
    client.post("/clientes", json=VALID_PAYLOAD)

    response = client.post("/clientes", json=VALID_PAYLOAD)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "dni", "message": "El cliente ya se encuentra registrado"}
    ]
