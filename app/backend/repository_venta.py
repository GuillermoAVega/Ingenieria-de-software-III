from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.backend.models import Customer, Product, Sale, SaleItem, SaleStatus


def create_sale(
    session: Session,
    customer: Customer,
    items: list[tuple[Product, int, float]],
) -> Sale:
    total = sum(quantity * unit_price for _, quantity, unit_price in items)

    sale = Sale(
        customer_id=customer.id,
        sale_date=datetime.now(timezone.utc),
        total=total,
        status=SaleStatus.CONFIRMED,
    )
    session.add(sale)
    session.flush()

    for product, quantity, unit_price in items:
        session.add(
            SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
            )
        )
        product.stock -= quantity

    session.commit()
    session.refresh(sale)
    return sale
