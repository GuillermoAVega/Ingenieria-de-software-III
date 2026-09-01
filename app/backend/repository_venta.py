from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.backend import core, core_venta
from app.backend.models import Customer, Product, Sale, SaleItem, SaleStatus


def find_by_id(session: Session, sale_id: int) -> Sale | None:
    return session.query(Sale).filter_by(id=sale_id).first()


def find_sales_by_customer_dni(
    session: Session, dni: str
) -> tuple[bool, list[Sale]]:
    normalized_dni = core.try_normalize_dni(dni)
    if normalized_dni is None:
        return False, []

    customer_ids = [
        customer.id
        for customer in session.query(Customer).filter(Customer.dni == normalized_dni).all()
    ]
    if not customer_ids:
        return False, []

    sales = (
        session.query(Sale)
        .filter(Sale.customer_id.in_(customer_ids))
        .order_by(Sale.sale_date.desc())
        .all()
    )
    return True, sales


def list_sales(
    session: Session,
    dni: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[tuple[Sale, Customer]], bool]:
    rows = (
        session.query(Sale, Customer)
        .join(Customer, Sale.customer_id == Customer.id)
        .filter(Sale.status == SaleStatus.CONFIRMED)
        .all()
    )

    matching = [
        (sale, customer)
        for sale, customer in rows
        if (date_from is None or sale.sale_date.date() >= date_from)
        and (date_to is None or sale.sale_date.date() <= date_to)
        and core_venta.matches_dni(customer.dni, dni)
    ]

    matching.sort(key=lambda row: row[0].sale_date, reverse=True)

    start = (page - 1) * page_size
    end = start + page_size
    page_items = matching[start:end]
    has_next = len(matching) > end

    return page_items, has_next


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
        status=SaleStatus.DRAFT,
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

    session.commit()
    session.refresh(sale)
    return sale


def create_confirmed_sale(
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


def replace_sale_items(
    session: Session,
    sale_id: int,
    items: list[tuple[Product, int, float]],
) -> tuple[Sale | None, str | None]:
    sale = session.query(Sale).filter_by(id=sale_id).first()
    if sale is None:
        return None, "NOT_FOUND"

    if sale.status != SaleStatus.DRAFT:
        return sale, "NOT_DRAFT"

    session.query(SaleItem).filter_by(sale_id=sale.id).delete()

    for product, quantity, unit_price in items:
        session.add(
            SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
            )
        )

    sale.total = sum(quantity * unit_price for _, quantity, unit_price in items)

    session.commit()
    session.refresh(sale)
    return sale, None


def close_sale(session: Session, sale_id: int) -> tuple[Sale | None, str | None]:
    sale = session.query(Sale).filter_by(id=sale_id).first()
    if sale is None:
        return None, "NOT_FOUND"

    if sale.status != SaleStatus.DRAFT:
        return sale, "NOT_DRAFT"

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    if not items:
        return sale, "EMPTY_ITEMS"

    products = [session.query(Product).filter_by(id=item.product_id).one() for item in items]
    for item, product in zip(items, products):
        if item.quantity > product.stock:
            return sale, "INSUFFICIENT_STOCK"

    for item, product in zip(items, products):
        product.stock -= item.quantity

    sale.status = SaleStatus.CONFIRMED
    session.commit()
    session.refresh(sale)
    return sale, None


def cancel_sale(session: Session, sale_id: int) -> tuple[Sale | None, str | None]:
    sale = session.query(Sale).filter_by(id=sale_id).first()
    if sale is None:
        return None, "NOT_FOUND"

    if sale.status == SaleStatus.CANCELLED:
        return sale, "ALREADY_CANCELLED"

    if sale.status == SaleStatus.DRAFT:
        return sale, "DRAFT"

    items = session.query(SaleItem).filter_by(sale_id=sale.id).all()
    for item in items:
        product = session.query(Product).filter_by(id=item.product_id).one()
        product.stock += item.quantity

    sale.status = SaleStatus.CANCELLED
    session.commit()
    session.refresh(sale)
    return sale, None
