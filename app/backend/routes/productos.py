from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.backend import core, core_producto, repository_producto
from app.backend.database import get_session
from app.backend.models import Product

router = APIRouter()

SUCCESS_MESSAGE = "Producto registrado exitosamente"
REQUIRED_FIELD_MESSAGE = "El campo es obligatorio"
POSITIVE_NUMBER_MESSAGE = "El valor debe ser un número positivo"
DUPLICATE_SKU_MESSAGE = "El código de producto está duplicado"
PRODUCT_NOT_FOUND_MESSAGE = "Producto no encontrado"
BAJA_SUCCESS_MESSAGE = "Producto dado de baja exitosamente"
EDICION_SUCCESS_MESSAGE = "Producto modificado exitosamente"

_REQUIRED_FIELDS = ("sku", "name", "brand", "unit_price", "stock")
_TEXT_FIELDS = ("sku", "name", "brand", "description")

_EDICION_REQUIRED_FIELDS = ("name", "brand", "unit_price", "stock")
_EDICION_TEXT_FIELDS = ("name", "brand", "description")


def _serialize_product(product: Product) -> dict[str, Any]:
    return {
        "sku": product.sku,
        "name": product.name,
        "brand": product.brand,
        "description": product.description,
        "unit_price": product.unit_price,
        "stock": product.stock,
        "status": product.status.value,
    }


def _normalize_payload(payload: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for field in _TEXT_FIELDS:
        raw_value = payload.get(field)
        value = raw_value if isinstance(raw_value, str) else ""
        normalized[field] = core.trim_leading_trailing_space(value)
    for field in ("unit_price", "stock"):
        raw_value = payload.get(field)
        normalized[field] = raw_value if isinstance(raw_value, str) else ""
    return normalized


def _validate_fields(values: dict[str, str]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    for field in _REQUIRED_FIELDS:
        if not values[field]:
            errors.append({"field": field, "message": REQUIRED_FIELD_MESSAGE})

    if values["unit_price"] and not core_producto.validate_positive_number(
        values["unit_price"]
    ):
        errors.append({"field": "unit_price", "message": POSITIVE_NUMBER_MESSAGE})
    if values["stock"] and not core_producto.validate_positive_integer(
        values["stock"]
    ):
        errors.append({"field": "stock", "message": POSITIVE_NUMBER_MESSAGE})

    return errors


def _normalize_edit_payload(payload: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for field in _EDICION_TEXT_FIELDS:
        raw_value = payload.get(field)
        value = raw_value if isinstance(raw_value, str) else ""
        normalized[field] = core.trim_leading_trailing_space(value)
    for field in ("unit_price", "stock"):
        raw_value = payload.get(field)
        normalized[field] = raw_value if isinstance(raw_value, str) else ""
    return normalized


def _validate_edit_fields(values: dict[str, str]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    for field in _EDICION_REQUIRED_FIELDS:
        if not values[field]:
            errors.append({"field": field, "message": REQUIRED_FIELD_MESSAGE})

    if values["unit_price"] and not core_producto.validate_positive_number(
        values["unit_price"]
    ):
        errors.append({"field": "unit_price", "message": POSITIVE_NUMBER_MESSAGE})
    if values["stock"] and not core_producto.validate_positive_integer(
        values["stock"]
    ):
        errors.append({"field": "stock", "message": POSITIVE_NUMBER_MESSAGE})

    return errors


@router.post("/productos")
def alta_producto(
    payload: dict[str, Any], session: Session = Depends(get_session)
) -> JSONResponse:
    values = _normalize_payload(payload)
    errors = _validate_fields(values)

    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})

    if repository_producto.sku_exists(session, values["sku"]):
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "sku", "message": DUPLICATE_SKU_MESSAGE}]},
        )

    product = repository_producto.create_product(
        session,
        sku=values["sku"],
        name=values["name"],
        brand=values["brand"],
        description=values["description"],
        unit_price=values["unit_price"],
        stock=values["stock"],
    )

    return JSONResponse(
        status_code=201,
        content={
            "message": SUCCESS_MESSAGE,
            "product": _serialize_product(product),
        },
    )


@router.get("/productos")
def listar_productos(
    q: str | None = None,
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
) -> JSONResponse:
    products, has_next = repository_producto.list_products(session, query=q, page=page)

    return JSONResponse(
        status_code=200,
        content={
            "products": [_serialize_product(product) for product in products],
            "page": page,
            "has_next": has_next,
        },
    )


@router.get("/productos/{sku}")
def buscar_producto(
    sku: str, session: Session = Depends(get_session)
) -> JSONResponse:
    product = repository_producto.find_by_sku(session, sku)

    if product is None:
        return JSONResponse(
            status_code=404,
            content={
                "errors": [{"field": "sku", "message": PRODUCT_NOT_FOUND_MESSAGE}]
            },
        )

    return JSONResponse(
        status_code=200,
        content={"product": _serialize_product(product)},
    )


@router.patch("/productos/{sku}/baja")
def baja_producto(
    sku: str, session: Session = Depends(get_session)
) -> JSONResponse:
    product = repository_producto.deactivate_by_sku(session, sku)

    if product is None:
        return JSONResponse(
            status_code=404,
            content={
                "errors": [{"field": "sku", "message": PRODUCT_NOT_FOUND_MESSAGE}]
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "message": BAJA_SUCCESS_MESSAGE,
            "product": _serialize_product(product),
        },
    )


@router.put("/productos/{sku}/editar")
def editar_producto(
    sku: str, payload: dict[str, Any], session: Session = Depends(get_session)
) -> JSONResponse:
    product = repository_producto.find_by_sku(session, sku)

    if product is None:
        return JSONResponse(
            status_code=404,
            content={
                "errors": [{"field": "sku", "message": PRODUCT_NOT_FOUND_MESSAGE}]
            },
        )

    values = _normalize_edit_payload(payload)
    errors = _validate_edit_fields(values)

    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})

    updated = repository_producto.update_product(
        session,
        product,
        name=values["name"],
        brand=values["brand"],
        description=values["description"],
        unit_price=values["unit_price"],
        stock=values["stock"],
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": EDICION_SUCCESS_MESSAGE,
            "product": _serialize_product(updated),
        },
    )
