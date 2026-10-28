import os
from datetime import date

# Debe fijarse antes de importar src.main (load_dotenv no sobrescribe)
os.environ["ENV"] = "test"
os.environ["DB_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import configurar_sqlite, get_db
from src.main import app
from src.models import ModeloBase
from src.productos import registro  # noqa: F401  (carga los mappers de todos los subtipos)
from src.productos.services import obtener_hoy

# Fecha fija para las pruebas (el fixture `cliente` sobrescribe obtener_hoy con ella)
HOY_FIJO = date(2026, 6, 15)


@pytest.fixture
def HOY():
    return HOY_FIJO


@pytest.fixture
def motor():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    configurar_sqlite(motor)
    ModeloBase.metadata.create_all(bind=motor)
    yield motor
    ModeloBase.metadata.drop_all(bind=motor)
    motor.dispose()


@pytest.fixture
def sesion(motor):
    sesion = sessionmaker(autocommit=False, autoflush=False, bind=motor)()
    yield sesion
    sesion.close()


@pytest.fixture
def cliente(motor):
    SesionPrueba = sessionmaker(autocommit=False, autoflush=False, bind=motor)

    def _obtener_sesion_prueba():
        sesion = SesionPrueba()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[get_db] = _obtener_sesion_prueba
    app.dependency_overrides[obtener_hoy] = lambda: HOY_FIJO
    yield TestClient(app)
    app.dependency_overrides.clear()
