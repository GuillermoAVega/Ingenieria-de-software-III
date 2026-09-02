from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.backend import repository, repository_producto, repository_venta
from app.backend.models import Sale, SaleStatus
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

# Días hacia atrás (desde hoy) de cada venta, para que el historial quede
# repartido a lo largo de ~9 meses y los filtros por rango de fechas se
# puedan probar de verdad: hay ventas de hoy, de esta semana, del mes
# pasado y de bastante más atrás, con algunos días que concentran dos
# ventas (0 y 1, 45 y 46) para probar los extremos inclusivos del rango.
SALE_DAYS_AGO: list[int] = [
    0, 1, 0, 3, 6, 9, 13, 18, 24, 31, 38, 45, 45, 52, 60,
    74, 88, 103, 119, 136, 154, 173, 193, 214, 236,
]

# Horas del día de cada venta, para que dos ventas del mismo día no
# queden con la misma marca de tiempo.
_SALE_HOURS = [9, 11, 13, 15, 17, 19]

# Posiciones (en el orden del listado) que quedan Anuladas, para poder
# ver en el listado la mezcla de estados Confirmada/Anulada.
CANCELLED_SALE_INDEXES: set[int] = {3, 11, 18}


def _sale_date_for(index: int) -> datetime:
    """Fecha ficticia de la venta que ocupa la posición `index`."""
    days_ago = SALE_DAYS_AGO[index % len(SALE_DAYS_AGO)]
    hour = _SALE_HOURS[index % len(_SALE_HOURS)]
    fecha = datetime.now() - timedelta(days=days_ago)
    return fecha.replace(hour=hour, minute=(index * 7) % 60, second=0, microsecond=0)


def aplicar_fechas_ficticias(session: Session) -> int:
    """Reparte las fechas de `SALE_DAYS_AGO` sobre las ventas existentes.

    No crea ni borra ventas: solo reescribe `sale_date`, así se puede
    correr sobre una base ya cargada. Es idempotente salvo por el
    desplazamiento del "hoy" de cada corrida.
    """
    sales = session.query(Sale).order_by(Sale.id).all()

    updated = 0
    for index, sale in enumerate(sales):
        nueva_fecha = _sale_date_for(index)
        if sale.sale_date != nueva_fecha:
            sale.sale_date = nueva_fecha
            updated += 1

    session.commit()
    return updated


def anular_ventas_ficticias(session: Session) -> int:
    """Anula las ventas de `CANCELLED_SALE_INDEXES` (repone su stock)."""
    sales = session.query(Sale).order_by(Sale.id).all()

    cancelled = 0
    for index, sale in enumerate(sales):
        if index not in CANCELLED_SALE_INDEXES:
            continue
        if sale.status != SaleStatus.CONFIRMED:
            continue
        _, error = repository_venta.cancel_sale(session, sale.id)
        if error is None:
            cancelled += 1

    return cancelled


def seed_ventas_ficticias(session: Session) -> int:
    existing_sales = session.query(Sale).count()
    if existing_sales >= len(SALE_PLANS):
        return 0

    created = 0
    for offset, (customer_dni, items_plan) in enumerate(SALE_PLANS[existing_sales:]):
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
            sale.sale_date = _sale_date_for(existing_sales + offset)
            session.commit()
            created += 1

    return created


def main() -> None:
    from app.backend.database import Base, create_db_engine, create_session_factory

    engine = create_db_engine()
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()
    try:
        created = seed_ventas_ficticias(session)
        fechas = aplicar_fechas_ficticias(session)
        anuladas = anular_ventas_ficticias(session)
        print(f"Ventas ficticias insertadas: {created}")
        print(f"Fechas repartidas sobre ventas existentes: {fechas}")
        print(f"Ventas pasadas a Anulada: {anuladas}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
