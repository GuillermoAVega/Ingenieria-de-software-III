from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend import core, core_producto
from app.backend.models import Product, ProductStatus


def sku_exists(session: Session, sku: str) -> bool:
    normalized_sku = core.normalize_search_text(sku)
    return (
        session.query(Product)
        .filter(
            func.lower(Product.sku) == normalized_sku,
            Product.status == ProductStatus.ACTIVE,
        )
        .first()
        is not None
    )


def find_by_sku(session: Session, sku: str) -> Product | None:
    normalized_sku = core.normalize_search_text(sku)
    return (
        session.query(Product)
        .filter(func.lower(Product.sku) == normalized_sku)
        .order_by(Product.status != ProductStatus.ACTIVE)
        .first()
    )


def deactivate_by_sku(session: Session, sku: str) -> Product | None:
    product = find_by_sku(session, sku)
    if product is None:
        return None
    product.status = ProductStatus.INACTIVE
    session.commit()
    session.refresh(product)
    return product


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
        status=core_producto.initial_status(),
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
