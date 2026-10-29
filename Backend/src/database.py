import os
from dotenv import load_dotenv
from sqlalchemy import Boolean, create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(os.getenv("DB_URL"), connect_args={"check_same_thread": False})
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
    # Para usar restricciones de FK en SQLite, debemos habilitar la siguiente opción:
    db.execute(text("PRAGMA foreign_keys = ON"))
    try:
        yield db
    finally:
        db.close()