import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
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

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
