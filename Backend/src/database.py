import os
from dotenv import load_dotenv
from sqlalchemy import Boolean, create_engine, inspect, text, event
from sqlalchemy.orm import sessionmaker

load_dotenv()


def configurar_sqlite(engine):
    """Configura SQLite: claves foráneas activas y transacciones BEGIN IMMEDIATE."""

    @event.listens_for(engine, "connect")
    def al_conectar(dbapi_connection, connection_record):
        # Control manual de transacciones: pysqlite no emite BEGIN por su cuenta
        dbapi_connection.isolation_level = None
        # Para usar restricciones de FK en SQLite debemos habilitar esta opción
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    @event.listens_for(engine, "begin")
    def al_iniciar_transaccion(conn):
        # Serializa los escritores y evita condiciones de carrera check-then-act
        conn.exec_driver_sql("BEGIN IMMEDIATE")

    return engine


engine = configurar_sqlite(
    create_engine(os.getenv("DB_URL"), connect_args={"check_same_thread": False})
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def migrar_detalle_reserva_legacy(database_engine=engine):
    from src.detalleReserva.models import DetalleReserva

    with database_engine.begin() as connection:
        inspector = inspect(connection)
        if "detalle_reserva" not in inspector.get_table_names():
            return

        columns = {
            column["name"]
            for column in inspector.get_columns("detalle_reserva")
        }
        if {"reserva_id", "producto_id", "cantidad_producto"}.issubset(columns):
            return

        if not {"reserva_id", "mesa_id"}.issubset(columns):
            raise RuntimeError(
                "La tabla detalle_reserva tiene un esquema no reconocido"
            )

        legacy_table = "detalle_reserva_legacy_mesas"
        if legacy_table in inspector.get_table_names():
            raise RuntimeError(
                f"No se puede migrar detalle_reserva: ya existe {legacy_table}"
            )

        connection.execute(text(
            "INSERT OR IGNORE INTO reserva_mesas (reserva_id, mesa_id) "
            "SELECT reserva_id, mesa_id FROM detalle_reserva"
        ))
        connection.execute(text(
            "ALTER TABLE detalle_reserva "
            "RENAME TO detalle_reserva_legacy_mesas"
        ))

    DetalleReserva.__table__.create(bind=database_engine)


def migrar_estado_reserva_legacy(database_engine=engine):
    with database_engine.begin() as connection:
        inspector = inspect(connection)
        if "reservas" not in inspector.get_table_names():
            return

        estado_column = next(
            (
                column
                for column in inspector.get_columns("reservas")
                if column["name"] == "estado"
            ),
            None,
        )
        if estado_column is None or not isinstance(
            estado_column["type"],
            Boolean,
        ):
            return

        connection.execute(text(
            "UPDATE reservas "
            "SET estado = CASE WHEN estado = 1 "
            "THEN 'pendiente' ELSE 'cancelada' END "
            "WHERE estado IN (0, 1)"
        ))


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
