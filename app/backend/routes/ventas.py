from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.backend import core_producto, repository, repository_producto, repository_venta
from app.backend.database import get_session
from app.backend.models import Customer, Product, Sale, SaleItem

router = APIRouter()

SUCCESS_MESSAGE = "Venta registrada exitosamente"
CUSTOMER_NOT_FOUND_MESSAGE = "Cliente no encontrado"
PRODUCT_NOT_FOUND_MESSAGE = "Producto no encontrado"
POSITIVE_NUMBER_MESSAGE = "El valor debe ser un número positivo"
EMPTY_ITEMS_MESSAGE = "La venta debe tener al menos un ítem"
SALE_NOT_FOUND_MESSAGE = "Venta no encontrada"
CANCEL_SUCCESS_MESSAGE = "Venta anulada exitosamente"
ALREADY_CANCELLED_MESSAGE = "La venta ya se encuentra anulada"


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


@router.post("/ventas")
def registrar_venta(
    payload: dict[str, Any], session: Session = Depends(get_session)
) -> JSONResponse:
    errors: list[dict[str, str]] = []

    dni = payload.get("dni")
    customer = repository.find_by_dni(session, dni) if isinstance(dni, str) and dni else None
    if customer is None:
        errors.append({"field": "dni", "message": CUSTOMER_NOT_FOUND_MESSAGE})

    items_payload = payload.get("items")
    if not isinstance(items_payload, list) or not items_payload:
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

        resolved_items.append((product, int(quantity_raw), float(unit_price_raw)))

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
    sale, already_cancelled = repository_venta.cancel_sale(session, sale_id)

    if sale is None:
        return JSONResponse(
            status_code=404,
            content={"errors": [{"field": "id", "message": SALE_NOT_FOUND_MESSAGE}]},
        )

    if already_cancelled:
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "id", "message": ALREADY_CANCELLED_MESSAGE}]},
        )

    return JSONResponse(
        status_code=200,
        content={
            "message": CANCEL_SUCCESS_MESSAGE,
            "sale": _serialize_sale(session, sale),
        },
    )
