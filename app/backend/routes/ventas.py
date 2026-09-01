from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.backend import core_producto, core_venta, repository, repository_producto, repository_venta
from app.backend.database import get_session
from app.backend.models import Customer, Product, ProductStatus, Sale, SaleItem, SaleStatus

router = APIRouter()

SUCCESS_MESSAGE = "Venta registrada exitosamente"
CUSTOMER_NOT_FOUND_MESSAGE = "Cliente no encontrado"
PRODUCT_NOT_FOUND_MESSAGE = "Producto no encontrado"
INACTIVE_PRODUCT_MESSAGE = "El producto no está disponible para la venta"
INSUFFICIENT_STOCK_MESSAGE = "No hay stock suficiente para completar la operación"
POSITIVE_NUMBER_MESSAGE = "El valor debe ser un número positivo"
EMPTY_ITEMS_MESSAGE = "La venta debe tener al menos un ítem"
SALE_NOT_FOUND_MESSAGE = "Venta no encontrada"
CANCEL_SUCCESS_MESSAGE = "Venta anulada exitosamente"
ALREADY_CANCELLED_MESSAGE = "La venta ya se encuentra anulada"
CANNOT_CANCEL_DRAFT_MESSAGE = "No se puede anular una venta en Borrador"
NOT_DRAFT_MESSAGE = "La venta ya no admite modificaciones"
NOT_DRAFT_TO_CLOSE_MESSAGE = "La venta ya no se encuentra en Borrador"
DETAIL_UPDATED_MESSAGE = "Detalle actualizado exitosamente"
CLOSE_SUCCESS_MESSAGE = "Venta cerrada exitosamente"
INVALID_DATE_RANGE_MESSAGE = "El rango de fechas es inválido"


def _serialize_sale(session: Session, sale: Sale) -> dict[str, Any]:
    customer = session.query(Customer).filter_by(id=sale.customer_id).one()
    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()

    serialized_items = []
    for item in items:
        product = session.query(Product).filter_by(id=item.product_id).one()
        serialized_items.append(
            {
                "sku": product.sku,
                "name": product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.quantity * item.unit_price,
            }
        )

    return {
        "id": sale.id,
        "customer": {
            "dni": customer.dni,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
        },
        "sale_date": sale.sale_date.isoformat(),
        "items": serialized_items,
        "total": sale.total,
        "status": sale.status.value,
    }


def _serialize_sale_summary(sale: Sale, customer: Customer) -> dict[str, Any]:
    return {
        "id": sale.id,
        "sale_date": sale.sale_date.isoformat(),
        "customer": {
            "dni": customer.dni,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
        },
        "total": sale.total,
    }


def _resolve_items(
    session: Session,
    items_payload: Any,
    *,
    require_non_empty: bool,
    check_product_active: bool,
    check_stock: bool,
) -> tuple[list[tuple[Product, int, float]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []

    if not isinstance(items_payload, list) or (require_non_empty and not items_payload):
        errors.append({"field": "items", "message": EMPTY_ITEMS_MESSAGE})
        items_payload = []

    resolved_items: list[tuple[Product, int, float]] = []
    for index, item in enumerate(items_payload):
        sku = item.get("sku") if isinstance(item, dict) else None
        quantity_raw = item.get("quantity") if isinstance(item, dict) else None
        unit_price_raw = item.get("unit_price") if isinstance(item, dict) else None

        product = (
            repository_producto.find_by_sku(session, sku)
            if isinstance(sku, str) and sku
            else None
        )
        if product is None:
            errors.append(
                {"field": f"items[{index}].sku", "message": PRODUCT_NOT_FOUND_MESSAGE}
            )
            continue

        if check_product_active and product.status != ProductStatus.ACTIVE:
            errors.append(
                {"field": f"items[{index}].sku", "message": INACTIVE_PRODUCT_MESSAGE}
            )
            continue

        if not isinstance(quantity_raw, str) or not core_producto.validate_positive_integer(
            quantity_raw
        ):
            errors.append(
                {
                    "field": f"items[{index}].quantity",
                    "message": POSITIVE_NUMBER_MESSAGE,
                }
            )
            continue

        quantity = int(quantity_raw)

        if check_stock and quantity > product.stock:
            errors.append(
                {"field": f"items[{index}].quantity", "message": INSUFFICIENT_STOCK_MESSAGE}
            )
            continue

        resolved_items.append((product, quantity, float(unit_price_raw)))

    return resolved_items, errors


@router.post("/ventas")
def registrar_venta(
    payload: dict[str, Any], session: Session = Depends(get_session)
) -> JSONResponse:
    errors: list[dict[str, str]] = []

    dni = payload.get("dni")
    customer = repository.find_by_dni(session, dni) if isinstance(dni, str) and dni else None
    if customer is None:
        errors.append({"field": "dni", "message": CUSTOMER_NOT_FOUND_MESSAGE})

    resolved_items, item_errors = _resolve_items(
        session,
        payload.get("items"),
        require_non_empty=True,
        check_product_active=False,
        check_stock=False,
    )
    errors.extend(item_errors)

    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})

    sale = repository_venta.create_sale(session, customer, resolved_items)

    return JSONResponse(
        status_code=201,
        content={
            "message": SUCCESS_MESSAGE,
            "sale": _serialize_sale(session, sale),
        },
    )


@router.get("/ventas")
def listar_ventas(
    dni: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(1, ge=1),
    session: Session = Depends(get_session),
) -> JSONResponse:
    if not core_venta.is_valid_date_range(date_from, date_to):
        return JSONResponse(
            status_code=422,
            content={
                "errors": [{"field": "date_range", "message": INVALID_DATE_RANGE_MESSAGE}]
            },
        )

    rows, has_next = repository_venta.list_sales(
        session, dni=dni, date_from=date_from, date_to=date_to, page=page
    )

    return JSONResponse(
        status_code=200,
        content={
            "sales": [_serialize_sale_summary(sale, customer) for sale, customer in rows],
            "page": page,
            "has_next": has_next,
        },
    )


@router.get("/ventas/{sale_id}")
def buscar_venta(sale_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    sale = repository_venta.find_by_id(session, sale_id)

    if sale is None:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"field": "id", "message": SALE_NOT_FOUND_MESSAGE}]},
        )

    return JSONResponse(
        status_code=200,
        content={"sale": _serialize_sale(session, sale)},
    )


@router.patch("/ventas/{sale_id}/anular")
def anular_venta(sale_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    sale, error = repository_venta.cancel_sale(session, sale_id)

    if sale is None:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"field": "id", "message": SALE_NOT_FOUND_MESSAGE}]},
        )

    if error == "ALREADY_CANCELLED":
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "id", "message": ALREADY_CANCELLED_MESSAGE}]},
        )

    if error == "DRAFT":
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "id", "message": CANNOT_CANCEL_DRAFT_MESSAGE}]},
        )

    return JSONResponse(
        status_code=200,
        content={
            "message": CANCEL_SUCCESS_MESSAGE,
            "sale": _serialize_sale(session, sale),
        },
    )


@router.put("/ventas/{sale_id}/detalle")
def reemplazar_detalle_venta(
    sale_id: int, payload: dict[str, Any], session: Session = Depends(get_session)
) -> JSONResponse:
    sale = repository_venta.find_by_id(session, sale_id)
    if sale is None:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"field": "id", "message": SALE_NOT_FOUND_MESSAGE}]},
        )

    if sale.status != SaleStatus.DRAFT:
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "id", "message": NOT_DRAFT_MESSAGE}]},
        )

    resolved_items, errors = _resolve_items(
        session,
        payload.get("items"),
        require_non_empty=False,
        check_product_active=True,
        check_stock=True,
    )

    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})

    updated_sale, _ = repository_venta.replace_sale_items(session, sale_id, resolved_items)

    return JSONResponse(
        status_code=200,
        content={
            "message": DETAIL_UPDATED_MESSAGE,
            "sale": _serialize_sale(session, updated_sale),
        },
    )


@router.patch("/ventas/{sale_id}/cerrar")
def cerrar_venta(sale_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    sale, error = repository_venta.close_sale(session, sale_id)

    if sale is None:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"field": "id", "message": SALE_NOT_FOUND_MESSAGE}]},
        )

    if error == "NOT_DRAFT":
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "id", "message": NOT_DRAFT_TO_CLOSE_MESSAGE}]},
        )

    if error == "EMPTY_ITEMS":
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "items", "message": EMPTY_ITEMS_MESSAGE}]},
        )

    if error == "INSUFFICIENT_STOCK":
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "items", "message": INSUFFICIENT_STOCK_MESSAGE}]},
        )

    return JSONResponse(
        status_code=200,
        content={
            "message": CLOSE_SUCCESS_MESSAGE,
            "sale": _serialize_sale(session, sale),
        },
    )
