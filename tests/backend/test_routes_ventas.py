from datetime import date, timedelta

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
    assert body["status"] == "Borrador"
    assert body["total"] == 701.0
    assert body["customer"]["dni"] == 30111222
    assert len(body["items"]) == 1
    assert body["items"][0]["sku"] == "ABC123"
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["subtotal"] == 701.0

    producto = client.get("/productos/ABC123").json()["product"]
    assert producto["stock"] == 100


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
    assert producto["stock"] == 1


def _registrar_venta(client, quantity="2"):
    client.post("/clientes", json=VALID_CLIENT_PAYLOAD)
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": quantity, "unit_price": "350.50"}],
    }
    response = client.post("/ventas", json=payload)
    return response.json()["sale"]["id"]


def _registrar_y_cerrar_venta(client, quantity="2"):
    sale_id = _registrar_venta(client, quantity=quantity)
    client.patch(f"/ventas/{sale_id}/cerrar")
    return sale_id


def test_buscar_venta_en_borrador_devuelve_sus_datos(client):
    sale_id = _registrar_venta(client)

    response = client.get(f"/ventas/{sale_id}")

    assert response.status_code == 200
    assert response.json()["sale"]["status"] == "Borrador"


def test_buscar_venta_confirmada_devuelve_sus_datos(client):
    sale_id = _registrar_y_cerrar_venta(client)

    response = client.get(f"/ventas/{sale_id}")

    assert response.status_code == 200
    assert response.json()["sale"]["status"] == "Confirmada"


def test_buscar_venta_anulada_informa_su_estado(client):
    sale_id = _registrar_y_cerrar_venta(client)
    client.patch(f"/ventas/{sale_id}/anular")

    response = client.get(f"/ventas/{sale_id}")

    assert response.status_code == 200
    assert response.json()["sale"]["status"] == "Anulada"


def test_buscar_venta_inexistente_devuelve_404(client):
    response = client.get("/ventas/999")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "id", "message": "Venta no encontrada"}
    ]


def test_anular_venta_exitosa_repone_stock(client):
    sale_id = _registrar_y_cerrar_venta(client, quantity="2")
    producto_antes = client.get("/productos/ABC123").json()["product"]
    assert producto_antes["stock"] == 98

    response = client.patch(f"/ventas/{sale_id}/anular")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Venta anulada exitosamente"
    assert body["sale"]["status"] == "Anulada"

    producto_despues = client.get("/productos/ABC123").json()["product"]
    assert producto_despues["stock"] == 100


def test_anular_venta_inexistente_devuelve_404(client):
    response = client.patch("/ventas/999/anular")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "id", "message": "Venta no encontrada"}
    ]


def test_anular_venta_ya_anulada_devuelve_422_sin_duplicar_stock(client):
    sale_id = _registrar_y_cerrar_venta(client, quantity="2")
    client.patch(f"/ventas/{sale_id}/anular")
    producto_tras_primera = client.get("/productos/ABC123").json()["product"]
    assert producto_tras_primera["stock"] == 100

    response = client.patch(f"/ventas/{sale_id}/anular")

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "id", "message": "La venta ya se encuentra anulada"}
    ]

    producto_tras_segunda = client.get("/productos/ABC123").json()["product"]
    assert producto_tras_segunda["stock"] == 100


def test_anular_venta_en_borrador_devuelve_422_sin_tocar_stock(client):
    sale_id = _registrar_venta(client, quantity="2")
    producto_antes = client.get("/productos/ABC123").json()["product"]
    assert producto_antes["stock"] == 100

    response = client.patch(f"/ventas/{sale_id}/anular")

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "id", "message": "No se puede anular una venta en Borrador"}
    ]

    producto_despues = client.get("/productos/ABC123").json()["product"]
    assert producto_despues["stock"] == 100


def test_reemplazar_detalle_venta_exitoso(client):
    sale_id = _registrar_venta(client, quantity="2")
    other_product = dict(VALID_PRODUCT_PAYLOAD, sku="XYZ999", unit_price="200", stock="50")
    client.post("/productos", json=other_product)

    payload = {"items": [{"sku": "XYZ999", "quantity": "3", "unit_price": "200"}]}
    response = client.put(f"/ventas/{sale_id}/detalle", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Detalle actualizado exitosamente"
    assert body["sale"]["total"] == 600.0
    assert len(body["sale"]["items"]) == 1
    assert body["sale"]["items"][0]["sku"] == "XYZ999"


def test_reemplazar_detalle_venta_inexistente_devuelve_404(client):
    response = client.put("/ventas/999/detalle", json={"items": []})

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "id", "message": "Venta no encontrada"}
    ]


def test_reemplazar_detalle_venta_no_editable_devuelve_422(client):
    sale_id = _registrar_y_cerrar_venta(client, quantity="2")

    response = client.put(f"/ventas/{sale_id}/detalle", json={"items": []})

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "id", "message": "La venta ya no admite modificaciones"}
    ]


def test_reemplazar_detalle_venta_admite_lista_vacia(client):
    sale_id = _registrar_venta(client, quantity="2")

    response = client.put(f"/ventas/{sale_id}/detalle", json={"items": []})

    assert response.status_code == 200
    body = response.json()["sale"]
    assert body["items"] == []
    assert body["total"] == 0


def test_reemplazar_detalle_venta_reporta_todos_los_errores_combinados(client):
    sale_id = _registrar_venta(client, quantity="2")
    inactive_product = dict(VALID_PRODUCT_PAYLOAD, sku="INACT1", unit_price="50", stock="10")
    client.post("/productos", json=inactive_product)
    client.patch("/productos/INACT1/baja")
    poco_stock = dict(VALID_PRODUCT_PAYLOAD, sku="POCO1", unit_price="10", stock="1")
    client.post("/productos", json=poco_stock)

    payload = {
        "items": [
            {"sku": "INACT1", "quantity": "1", "unit_price": "50"},
            {"sku": "POCO1", "quantity": "5", "unit_price": "10"},
            {"sku": "ABC123", "quantity": "0", "unit_price": "350.50"},
        ]
    }
    response = client.put(f"/ventas/{sale_id}/detalle", json=payload)

    assert response.status_code == 422
    campos = {error["field"] for error in response.json()["errors"]}
    assert campos == {"items[0].sku", "items[1].quantity", "items[2].quantity"}

    sin_cambios = client.get(f"/ventas/{sale_id}").json()["sale"]
    assert len(sin_cambios["items"]) == 1
    assert sin_cambios["items"][0]["sku"] == "ABC123"


def test_cerrar_venta_exitoso(client):
    sale_id = _registrar_venta(client, quantity="2")

    response = client.patch(f"/ventas/{sale_id}/cerrar")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Venta cerrada exitosamente"
    assert body["sale"]["status"] == "Confirmada"

    producto = client.get("/productos/ABC123").json()["product"]
    assert producto["stock"] == 98


def test_cerrar_venta_inexistente_devuelve_404(client):
    response = client.patch("/ventas/999/cerrar")

    assert response.status_code == 404
    assert response.json()["errors"] == [
        {"field": "id", "message": "Venta no encontrada"}
    ]


def test_cerrar_venta_ya_no_esta_en_borrador_devuelve_422(client):
    sale_id = _registrar_y_cerrar_venta(client, quantity="2")

    response = client.patch(f"/ventas/{sale_id}/cerrar")

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "id", "message": "La venta ya no se encuentra en Borrador"}
    ]


def test_cerrar_venta_con_detalle_vacio_devuelve_422(client):
    sale_id = _registrar_venta(client, quantity="2")
    client.put(f"/ventas/{sale_id}/detalle", json={"items": []})

    response = client.patch(f"/ventas/{sale_id}/cerrar")

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "items", "message": "La venta debe tener al menos un ítem"}
    ]


def test_cerrar_venta_con_stock_insuficiente_devuelve_422_sin_descontar(client):
    sale_id = _registrar_venta(client, quantity="2")

    other_payload = {
        "dni": "30111222",
        "items": [{"sku": "ABC123", "quantity": "99", "unit_price": "350.50"}],
    }
    otra_venta_id = client.post("/ventas", json=other_payload).json()["sale"]["id"]
    client.patch(f"/ventas/{otra_venta_id}/cerrar")

    response = client.patch(f"/ventas/{sale_id}/cerrar")

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "items", "message": "No hay stock suficiente para completar la operación"}
    ]

    sin_cambios = client.get(f"/ventas/{sale_id}").json()["sale"]
    assert sin_cambios["status"] == "Borrador"


def _registrar_cliente(client, dni):
    client.post(
        "/clientes",
        json=dict(VALID_CLIENT_PAYLOAD, dni=dni),
    )


def _registrar_y_confirmar_venta(client, dni="30111222", sku="ABC123"):
    _registrar_cliente(client, dni)
    if client.get(f"/productos/{sku}").status_code != 200:
        client.post("/productos", json=dict(VALID_PRODUCT_PAYLOAD, sku=sku, stock="10000"))
    payload = {"dni": dni, "items": [{"sku": sku, "quantity": "1", "unit_price": "350.50"}]}
    sale_id = client.post("/ventas", json=payload).json()["sale"]["id"]
    client.patch(f"/ventas/{sale_id}/cerrar")
    return sale_id


def test_listar_ventas_endpoint_devuelve_resumen_sin_items_ni_estado(client):
    sale_id = _registrar_y_confirmar_venta(client)

    response = client.get("/ventas")

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["has_next"] is False
    sale = next(s for s in body["sales"] if s["id"] == sale_id)
    assert sale["customer"]["dni"] == 30111222
    assert sale["total"] == 350.5
    assert "items" not in sale
    assert "status" not in sale


def test_listar_ventas_excluye_borrador_y_anulada(client):
    _registrar_cliente(client, "30111222")
    client.post("/productos", json=VALID_PRODUCT_PAYLOAD)
    draft_id = client.post(
        "/ventas",
        json={"dni": "30111222", "items": [{"sku": "ABC123", "quantity": "1", "unit_price": "350.50"}]},
    ).json()["sale"]["id"]

    cancelled_id = _registrar_y_confirmar_venta(client, dni="30111222", sku="ABC123")
    client.patch(f"/ventas/{cancelled_id}/anular")

    response = client.get("/ventas")

    ids = {s["id"] for s in response.json()["sales"]}
    assert draft_id not in ids
    assert cancelled_id not in ids


def test_listar_ventas_filtro_fechas(client):
    sale_id = _registrar_y_confirmar_venta(client)
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    incluye = client.get("/ventas", params={"date_from": today, "date_to": today})
    excluye = client.get("/ventas", params={"date_from": tomorrow})

    assert sale_id in {s["id"] for s in incluye.json()["sales"]}
    assert sale_id not in {s["id"] for s in excluye.json()["sales"]}


def test_listar_ventas_rango_de_fechas_invalido_devuelve_422(client):
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = client.get("/ventas", params={"date_from": tomorrow, "date_to": today})

    assert response.status_code == 422
    assert response.json()["errors"] == [
        {"field": "date_range", "message": "El rango de fechas es inválido"}
    ]


def test_listar_ventas_filtro_por_dni_parcial(client):
    sale_a = _registrar_y_confirmar_venta(client, dni="30111222", sku="AAA111")
    _registrar_y_confirmar_venta(client, dni="40222333", sku="BBB222")

    response = client.get("/ventas", params={"dni": "3011"})

    ids = {s["id"] for s in response.json()["sales"]}
    assert ids == {sale_a}


def test_listar_ventas_combina_dni_y_fecha(client):
    sale_a = _registrar_y_confirmar_venta(client, dni="30111222", sku="CCC333")
    today = date.today().isoformat()

    response = client.get("/ventas", params={"dni": "3011", "date_from": today, "date_to": today})

    ids = {s["id"] for s in response.json()["sales"]}
    assert ids == {sale_a}


def test_listar_ventas_sin_coincidencias_devuelve_lista_vacia(client):
    _registrar_y_confirmar_venta(client)

    response = client.get("/ventas", params={"dni": "99999999"})

    assert response.status_code == 200
    assert response.json()["sales"] == []


def test_listar_ventas_pagina_2_devuelve_el_resto(client):
    _registrar_cliente(client, "30111222")
    client.post("/productos", json=dict(VALID_PRODUCT_PAYLOAD, stock="10000"))
    for _ in range(25):
        payload = {
            "dni": "30111222",
            "items": [{"sku": "ABC123", "quantity": "1", "unit_price": "350.50"}],
        }
        sale_id = client.post("/ventas", json=payload).json()["sale"]["id"]
        client.patch(f"/ventas/{sale_id}/cerrar")

    response = client.get("/ventas", params={"page": 2})

    body = response.json()
    assert len(body["sales"]) == 5
    assert body["has_next"] is False
