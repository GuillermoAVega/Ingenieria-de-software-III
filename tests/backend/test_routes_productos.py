import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.backend.database import Base, create_db_engine, create_session_factory, get_session
from app.backend.routes.productos import router

VALID_PAYLOAD = {
    "sku": "ABC123",
    "name": "Coca-Cola 500ml",
    "brand": "Coca-Cola",
    "description": "Botella descartable",
    "unit_price": "350.50",
    "stock": "100",
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


def test_alta_producto_exitosa_crea_producto_y_devuelve_mensaje(client):
    response = client.post("/productos", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Producto registrado exitosamente"
    assert body["product"]["sku"] == "ABC123"
    assert body["product"]["unit_price"] == 350.5
    assert body["product"]["stock"] == 100


def test_alta_producto_exitosa_sin_descripcion(client):
    payload = dict(VALID_PAYLOAD)
    del payload["description"]

    response = client.post("/productos", json=payload)

    assert response.status_code == 201
    assert response.json()["product"]["description"] in (None, "")


def test_campos_obligatorios_vacios_devuelve_las_cinco_advertencias(client):
    payload = {
        "sku": "",
        "name": "",
        "brand": "",
        "description": "",
        "unit_price": "",
        "stock": "",
    }

    response = client.post("/productos", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"sku", "name", "brand", "unit_price", "stock"}


@pytest.mark.parametrize("unit_price", ["0", "-5", "abc"])
def test_unit_price_invalido_advierte_numero_positivo(client, unit_price):
    payload = dict(VALID_PAYLOAD, unit_price=unit_price)

    response = client.post("/productos", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "unit_price", "message": "El valor debe ser un número positivo"}
    ]


@pytest.mark.parametrize("stock", ["0", "-1", "5.5", "abc"])
def test_stock_invalido_advierte_numero_positivo(client, stock):
    payload = dict(VALID_PAYLOAD, stock=stock)

    response = client.post("/productos", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "stock", "message": "El valor debe ser un número positivo"}
    ]


def test_editar_ignora_sku_incluido_en_el_body(client):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = dict(EDICION_PAYLOAD, sku="OTRO999")

    response = client.put("/productos/ABC123/editar", json=payload)

    assert response.status_code == 200
    assert response.json()["product"]["sku"] == "ABC123"


def test_editar_multiples_errores_combinados_en_un_intento(client):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = dict(EDICION_PAYLOAD, unit_price="-5", stock="abc")

    response = client.put("/productos/ABC123/editar", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"unit_price", "stock"}


def test_sku_duplicado_exacto_bloquea_el_alta(client):
    client.post("/productos", json=VALID_PAYLOAD)

    response = client.post("/productos", json=VALID_PAYLOAD)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "sku", "message": "El código de producto está duplicado"}
    ]


def test_sku_duplicado_con_distinta_capitalizacion_bloquea_el_alta(client):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = dict(VALID_PAYLOAD, sku="abc123")

    response = client.post("/productos", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "sku", "message": "El código de producto está duplicado"}
    ]


def test_multiples_errores_de_formato_combinados_en_un_intento(client):
    payload = dict(VALID_PAYLOAD, unit_price="-5", stock="abc")

    response = client.post("/productos", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"unit_price", "stock"}


def test_unit_price_negativo_y_sku_duplicado_a_la_vez(client):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = dict(VALID_PAYLOAD, name="Otro nombre", unit_price="-5")

    response = client.post("/productos", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "unit_price", "message": "El valor debe ser un número positivo"}
    ]


def test_sku_y_nombre_con_espacios_se_recortan_antes_de_persistir(client):
    payload = dict(VALID_PAYLOAD, sku="  ABC123  ", name="  Coca-Cola 500ml  ")

    response = client.post("/productos", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["product"]["sku"] == "ABC123"
    assert body["product"]["name"] == "Coca-Cola 500ml"


def test_alta_producto_asigna_estado_activo_por_defecto(client):
    response = client.post("/productos", json=VALID_PAYLOAD)

    assert response.json()["product"]["status"] == "Activo"


def test_buscar_producto_activo_devuelve_sus_datos(client):
    client.post("/productos", json=VALID_PAYLOAD)

    response = client.get("/productos/ABC123")

    assert response.status_code == 200
    assert response.json()["product"]["status"] == "Activo"


def test_buscar_producto_inexistente_devuelve_404(client):
    response = client.get("/productos/ABC123")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "sku", "message": "Producto no encontrado"}
    ]


def test_baja_producto_activo_con_stock_alto_no_modifica_el_stock(client):
    payload = dict(VALID_PAYLOAD, stock="500")
    client.post("/productos", json=payload)

    response = client.patch("/productos/ABC123/baja")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Producto dado de baja exitosamente"
    assert body["product"]["status"] == "Inactivo"
    assert body["product"]["stock"] == 500


def test_baja_producto_inexistente_devuelve_404(client):
    response = client.patch("/productos/ABC123/baja")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "sku", "message": "Producto no encontrado"}
    ]


def test_baja_directa_sobre_producto_ya_inactivo_no_falla(client):
    client.post("/productos", json=VALID_PAYLOAD)
    client.patch("/productos/ABC123/baja")

    response = client.patch("/productos/ABC123/baja")

    assert response.status_code == 200
    assert response.json()["product"]["status"] == "Inactivo"


def test_alta_nueva_reutiliza_sku_de_producto_inactivo(client):
    client.post("/productos", json=VALID_PAYLOAD)
    client.patch("/productos/ABC123/baja")

    response = client.post("/productos", json=dict(VALID_PAYLOAD, name="Producto nuevo"))

    assert response.status_code == 201
    assert response.json()["product"]["name"] == "Producto nuevo"


def test_alta_nueva_sigue_bloqueada_contra_sku_de_producto_activo(client):
    client.post("/productos", json=VALID_PAYLOAD)

    response = client.post("/productos", json=dict(VALID_PAYLOAD, name="Otro"))

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "sku", "message": "El código de producto está duplicado"}
    ]


EDICION_PAYLOAD = {
    "name": "Coca-Cola 1L",
    "brand": "Coca-Cola",
    "description": "Botella retornable",
    "unit_price": "399.90",
    "stock": "80",
}


def test_editar_producto_activo_guarda_los_cambios(client):
    client.post("/productos", json=VALID_PAYLOAD)

    response = client.put("/productos/ABC123/editar", json=EDICION_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Producto modificado exitosamente"
    assert body["product"]["name"] == "Coca-Cola 1L"
    assert body["product"]["unit_price"] == 399.9
    assert body["product"]["stock"] == 80
    assert body["product"]["sku"] == "ABC123"
    assert body["product"]["status"] == "Activo"


def test_editar_producto_inactivo_guarda_los_cambios_sin_reactivarlo(client):
    client.post("/productos", json=VALID_PAYLOAD)
    client.patch("/productos/ABC123/baja")

    response = client.put("/productos/ABC123/editar", json=EDICION_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["product"]["status"] == "Inactivo"
    assert response.json()["product"]["name"] == "Coca-Cola 1L"


def test_editar_producto_inexistente_devuelve_404(client):
    response = client.put("/productos/ABC123/editar", json=EDICION_PAYLOAD)

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "sku", "message": "Producto no encontrado"}
    ]


def test_editar_con_campos_obligatorios_vacios_devuelve_cuatro_advertencias(client):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = {"name": "", "brand": "", "description": "", "unit_price": "", "stock": ""}

    response = client.put("/productos/ABC123/editar", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"name", "brand", "unit_price", "stock"}


@pytest.mark.parametrize("unit_price", ["0", "-5", "abc"])
def test_editar_unit_price_invalido_advierte_numero_positivo(client, unit_price):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = dict(EDICION_PAYLOAD, unit_price=unit_price)

    response = client.put("/productos/ABC123/editar", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "unit_price", "message": "El valor debe ser un número positivo"}
    ]


@pytest.mark.parametrize("stock", ["0", "-1", "5.5", "abc"])
def test_editar_stock_invalido_advierte_numero_positivo(client, stock):
    client.post("/productos", json=VALID_PAYLOAD)
    payload = dict(EDICION_PAYLOAD, stock=stock)

    response = client.put("/productos/ABC123/editar", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "stock", "message": "El valor debe ser un número positivo"}
    ]
