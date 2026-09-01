import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.backend.database import Base, create_db_engine, create_session_factory, get_session
from app.backend.routes.clientes import router as clientes_router
from app.backend.routes.productos import router as productos_router
from app.backend.routes.ventas import router as ventas_router

VALID_CLIENT_PAYLOAD = {
    "dni": "30111222",
    "first_name": "Juan",
    "last_name": "Perez",
    "email": "juan@dominio.com",
    "phone": "11-4444-5555",
}

VALID_PRODUCT_PAYLOAD = {
    "sku": "ABC123",
    "name": "Coca-Cola 500ml",
    "brand": "Coca-Cola",
    "description": "",
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
    app.include_router(clientes_router)
    app.include_router(productos_router)
    app.include_router(ventas_router)
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client


def test_registrar_venta_exitosa_con_un_item(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)

    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": "2", "unit_price": "350.50"}],
    }
    response = client.post("/ventas", json=payload)

    assert response.status_code == 201
    body = response.json()["sale"]
    assert body["status"] == "Confirmada"
    assert body["total"] == 701.0
    assert body["customer"]["dni"] == 30111222
    assert len(body["items"]) == 1
    assert body["items"][0]["sku"] == "ABC123"
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["subtotal"] == 701.0

    producto = client.get("/productos/ABC123").json()["product"]
    assert producto["stock"] == 98


def test_registrar_venta_exitosa_con_varios_items(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    other_product = dict(VALID_PRODUCT_PAYLOAD, sku="XYZ999", unit_price="200", stock="50")
    client.post("/productos", json=other_product)

    payload = {
        "dni": "30111222",
        "items": [
            {"sku": "ABC123", "quantity": "2", "unit_price": "350.50"},
            {"sku": "XYZ999", "quantity": "3", "unit_price": "200"},
        ],
    }
    response = client.post("/ventas", json=payload)

    assert response.status_code == 201
    body = response.json()["sale"]
    assert body["total"] == 2 * 350.5 + 3 * 200
    assert len(body["items"]) == 2


def test_registrar_venta_dni_inexistente_devuelve_422(client):
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": "2", "unit_price": "350.50"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "dni", "message": "Cliente no encontrado"}
    ]


def test_registrar_venta_sku_inexistente_devuelve_422_con_field_indexado(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ZZZ000", "quantity": "2", "unit_price": "350.50"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "items[0].sku", "message": "Producto no encontrado"}
    ]


@pytest.mark.parametrize("quantity", ["0", "-1", "5.5", "abc"])
def test_registrar_venta_cantidad_invalida_devuelve_422_con_field_indexado(client, quantity):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": quantity, "unit_price": "350.50"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "items[0].quantity", "message": "El valor debe ser un número positivo"}
    ]


def test_registrar_venta_detalle_vacio_devuelve_422(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    payload = {"dni": "30111222", "items": []}

    response = client.post("/ventas", json=payload)

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "items", "message": "La venta debe tener al menos un ítem"}
    ]


def test_registrar_venta_multiples_errores_combinados(client):
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ZZZ000", "quantity": "2", "unit_price": "10"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"dni", "items[0].sku"}


def test_registrar_venta_con_cliente_inactivo_se_registra_igual(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    client.patch("/clientes/30111222/baja")
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": "2", "unit_price": "350.50"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 201


def test_registrar_venta_con_producto_inactivo_se_registra_igual(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    client.patch("/productos/ABC123/baja")
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": "2", "unit_price": "350.50"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 201


def test_registrar_venta_con_cantidad_mayor_al_stock_se_registra_igual(client):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    poco_stock = dict(VALID_PRODUCT_PAYLOAD, stock="1")
    client.post("/productos", json=poco_stock)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": "5", "unit_price": "350.50"}],
    }

    response = client.post("/ventas", json=payload)

    assert response.status_code == 201
    producto = client.get("/productos/ABC123").json()["product"]
    assert producto["stock"] == -4
