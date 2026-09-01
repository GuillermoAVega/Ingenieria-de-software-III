from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend import core
from app.backend.models import Product


def sku_exists(session: Session, sku: str) -> bool:
    normalized_sku = core.normalize_search_text(sku)
    return (
        session.query(Product)
        .filter(func.lower(Product.sku) == normalized_sku)
        .first()
        is not None
    )


def create_product(
    session: Session,
    sku: str,
    name: str,
    brand: str,
    description: str,
    unit_price: str,
    stock: str,
) -> Product:
    product = Product(
        sku=sku,
        name=name,
        brand=brand,
        description=description,
        unit_price=float(unit_price),
        stock=int(stock),
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
