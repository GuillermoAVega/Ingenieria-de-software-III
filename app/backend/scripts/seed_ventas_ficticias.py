from sqlalchemy.orm import Session

from app.backend import repository, repository_producto, repository_venta
from app.backend.models import Sale
from app.backend.scripts.seed_clientes_ficticios import FICTITIOUS_CUSTOMERS
from app.backend.scripts.seed_productos_ficticios import FICTITIOUS_PRODUCTS

_CUSTOMER_DNIS = [customer["dni"] for customer in FICTITIOUS_CUSTOMERS]
_PRODUCT_SKUS = [product["sku"] for product in FICTITIOUS_PRODUCTS]

# 25 ventas ficticias repartidas entre los primeros 17 clientes: algunos
# clientes concentran varias compras y los últimos clientes quedan sin ventas,
# a propósito, para reflejar un escenario realista (no es 1 venta por cliente).
SALE_PLANS: list[tuple[str, list[tuple[str, int]]]] = [
    (
        _CUSTOMER_DNIS[index % 17],
        [
            (
                _PRODUCT_SKUS[(index * 3 + item) % len(_PRODUCT_SKUS)],
                1 + ((index + item) % 4),
            )
            for item in range(1 + (index % 3))
        ],
    )
    for index in range(25)
]


def seed_ventas_ficticias(session: Session) -> int:
    existing_sales = session.query(Sale).count()
    if existing_sales >= len(SALE_PLANS):
        return 0

    created = 0
    for customer_dni, items_plan in SALE_PLANS[existing_sales:]:
        customer = repository.find_by_dni(session, customer_dni)
        if customer is None:
            continue

        items = []
        for sku, quantity in items_plan:
            product = repository_producto.find_by_sku(session, sku)
            if product is None:
                continue
            items.append((product, quantity, product.unit_price))
        if not items:
            continue

        sale = repository_venta.create_sale(session, customer, items)
        _, error = repository_venta.close_sale(session, sale.id)
        if error is None:
            created += 1

    return created


def main() -> None:
    from app.backend.database import Base, create_db_engine, create_session_factory

    engine = create_db_engine()
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()
    try:
        created = seed_ventas_ficticias(session)
        print(f"Ventas ficticias insertadas: {created}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
