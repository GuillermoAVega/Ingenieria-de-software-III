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


def update_product(
    session: Session,
    product: Product,
    *,
    name: str,
    brand: str,
    description: str,
    unit_price: str,
    stock: str,
) -> Product:
    product.name = name
    product.brand = brand
    product.description = description
    product.unit_price = float(unit_price)
    product.stock = int(stock)
    session.commit()
    session.refresh(product)
    return product


def list_products(
    session: Session, query: str | None, page: int, page_size: int = 20
) -> tuple[list[Product], bool]:
    all_products = session.query(Product).order_by(Product.name).all()

    if query:
        normalized_query = core.normalize_search_text(
            core.trim_leading_trailing_space(query)
        )
        matching = [
            product
            for product in all_products
            if core_producto.matches_search(
                normalized_query, sku=product.sku, name=product.name
            )
        ]
    else:
        matching = all_products

    start = (page - 1) * page_size
    end = start + page_size
    page_items = matching[start:end]
    has_next = len(matching) > end

    return page_items, has_next


def search_for_venta(
    session: Session, query: str | None, limit: int = 20
) -> list[Product]:
    normalized_query = core.normalize_search_text(
        core.trim_leading_trailing_space(query or "")
    )
    if not normalized_query:
        return []

    active_products = (
        session.query(Product)
        .filter(Product.status == ProductStatus.ACTIVE)
        .order_by(Product.name)
        .all()
    )
    matching = [
        product
        for product in active_products
        if core_producto.matches_venta_search(
            normalized_query, name=product.name, description=product.description
        )
    ]

    return matching[:limit]


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
