from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.backend.models import Customer, Product, Sale, SaleItem, SaleStatus


def find_by_id(session: Session, sale_id: int) -> Sale | None:
    return session.query(Sale).filter_by(id=sale_id).first()


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


def cancel_sale(session: Session, sale_id: int) -> tuple[Sale | None, bool]:
    sale = session.query(Sale).filter_by(id=sale_id).first()
    if sale is None:
        return None, False

    if sale.status == SaleStatus.CANCELLED:
        return sale, True

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    for item in items:
        product = session.query(Product).filter_by(id=item.product_id).one()
        product.stock += item.quantity

    sale.status = SaleStatus.CANCELLED
    session.commit()
    session.refresh(sale)
    return sale, False
