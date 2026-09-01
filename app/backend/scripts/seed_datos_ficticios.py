from app.backend.database import Base, create_db_engine, create_session_factory
from app.backend.scripts.seed_clientes_ficticios import seed_clientes_ficticios
from app.backend.scripts.seed_productos_ficticios import seed_productos_ficticios
from app.backend.scripts.seed_ventas_ficticias import seed_ventas_ficticias


def main() -> None:
    engine = create_db_engine()
    Base.metadata.create_all(engine)
    session = create_session_factory(engine)()
    try:
        clientes = seed_clientes_ficticios(session)
        productos = seed_productos_ficticios(session)
        ventas = seed_ventas_ficticias(session)
        print(f"Clientes ficticios insertados: {clientes}")
        print(f"Productos ficticios insertados: {productos}")
        print(f"Ventas ficticias insertadas: {ventas}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
