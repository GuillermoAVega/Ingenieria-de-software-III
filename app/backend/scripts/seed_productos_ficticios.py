from sqlalchemy.orm import Session

from app.backend import core_producto, repository_producto

FICTITIOUS_PRODUCTS: list[dict[str, str]] = [
    {"sku": "SKU-0001", "name": "Notebook 15\"", "brand": "Lenovo", "description": "Notebook 15 pulgadas, 8GB RAM", "unit_price": "450000", "stock": "20"},
    {"sku": "SKU-0002", "name": "Mouse Óptico", "brand": "Logitech", "description": "Mouse óptico USB", "unit_price": "8500", "stock": "80"},
    {"sku": "SKU-0003", "name": "Teclado Mecánico", "brand": "Razer", "description": "Teclado mecánico retroiluminado", "unit_price": "35000", "stock": "40"},
    {"sku": "SKU-0004", "name": "Monitor 24\"", "brand": "Samsung", "description": "Monitor Full HD 24 pulgadas", "unit_price": "120000", "stock": "25"},
    {"sku": "SKU-0005", "name": "Auriculares Bluetooth", "brand": "Sony", "description": "Auriculares inalámbricos con cancelación de ruido", "unit_price": "60000", "stock": "35"},
    {"sku": "SKU-0006", "name": "Impresora Multifunción", "brand": "HP", "description": "Impresora, escáner y copiadora", "unit_price": "95000", "stock": "15"},
    {"sku": "SKU-0007", "name": "Router WiFi", "brand": "TP-Link", "description": "Router doble banda AC1200", "unit_price": "22000", "stock": "50"},
    {"sku": "SKU-0008", "name": "Disco SSD 480GB", "brand": "Kingston", "description": "Disco de estado sólido 480GB SATA", "unit_price": "38000", "stock": "60"},
    {"sku": "SKU-0009", "name": "Memoria RAM 8GB", "brand": "Corsair", "description": "Módulo de memoria DDR4 8GB", "unit_price": "25000", "stock": "70"},
    {"sku": "SKU-0010", "name": "Cargador USB-C", "brand": "Xiaomi", "description": "Cargador rápido 33W", "unit_price": "9000", "stock": "90"},
    {"sku": "SKU-0011", "name": "Cable HDMI 2m", "brand": "Genius", "description": "Cable HDMI 2 metros", "unit_price": "4500", "stock": "100"},
    {"sku": "SKU-0012", "name": "Mochila para Notebook", "brand": "Dell", "description": "Mochila acolchada hasta 15.6 pulgadas", "unit_price": "28000", "stock": "30"},
    {"sku": "SKU-0013", "name": "Silla Ergonómica", "brand": "Noblex", "description": "Silla de oficina con soporte lumbar", "unit_price": "150000", "stock": "10"},
    {"sku": "SKU-0014", "name": "Escritorio Compacto", "brand": "Noblex", "description": "Escritorio de melamina 100x60cm", "unit_price": "85000", "stock": "12"},
    {"sku": "SKU-0015", "name": "Lámpara LED de Escritorio", "brand": "Philips", "description": "Lámpara LED regulable", "unit_price": "15000", "stock": "45"},
    {"sku": "SKU-0016", "name": "Ventilador USB", "brand": "Genius", "description": "Mini ventilador USB de escritorio", "unit_price": "6000", "stock": "55"},
    {"sku": "SKU-0017", "name": "Parlante Bluetooth", "brand": "JBL", "description": "Parlante portátil resistente al agua", "unit_price": "42000", "stock": "38"},
    {"sku": "SKU-0018", "name": "Micrófono USB", "brand": "HP", "description": "Micrófono de condensador para streaming", "unit_price": "32000", "stock": "22"},
    {"sku": "SKU-0019", "name": "Webcam Full HD", "brand": "Logitech", "description": "Webcam 1080p con micrófono integrado", "unit_price": "27000", "stock": "40"},
    {"sku": "SKU-0020", "name": "Tablet 10\"", "brand": "Samsung", "description": "Tablet 10 pulgadas 64GB", "unit_price": "220000", "stock": "18"},
    {"sku": "SKU-0021", "name": "Smartphone Gama Media", "brand": "Motorola", "description": "Smartphone 128GB, cámara triple", "unit_price": "380000", "stock": "16"},
    {"sku": "SKU-0022", "name": "Smartwatch", "brand": "Xiaomi", "description": "Reloj inteligente con monitor cardíaco", "unit_price": "45000", "stock": "28"},
    {"sku": "SKU-0023", "name": "Cámara de Seguridad WiFi", "brand": "TP-Link", "description": "Cámara IP para interiores", "unit_price": "33000", "stock": "24"},
    {"sku": "SKU-0024", "name": "Pendrive 64GB", "brand": "SanDisk", "description": "Memoria USB 3.0 de 64GB", "unit_price": "7500", "stock": "100"},
    {"sku": "SKU-0025", "name": "Disco Externo 1TB", "brand": "Western Digital", "description": "Disco rígido externo portátil 1TB", "unit_price": "68000", "stock": "30"},
]


def _is_valid_product(data: dict[str, str]) -> bool:
    return (
        bool(data["sku"])
        and bool(data["name"])
        and bool(data["brand"])
        and core_producto.validate_positive_number(data["unit_price"])
        and core_producto.validate_positive_integer(data["stock"])
    )


def seed_productos_ficticios(session: Session) -> int:
    inserted = 0
    for data in FICTITIOUS_PRODUCTS:
        if not _is_valid_product(data):
            continue
        if repository_producto.find_by_sku(session, data["sku"]) is not None:
            continue
        repository_producto.create_product(session, **data)
        inserted += 1
    return inserted


def main() -> None:
    from app.backend.database import Base, create_db_engine, create_session_factory

    engine = create_db_engine()
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()
    try:
        inserted = seed_productos_ficticios(session)
        print(f"Productos ficticios insertados: {inserted}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
