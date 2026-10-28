from src.database import get_db
from src.main import app
from src.productos.services import obtener_hoy


def test_motor_en_memoria(motor):
    # La suite nunca debe tocar el archivo SQLite real
    assert str(motor.url) == "sqlite://"


def test_get_db_sobrescrito(cliente, sesion):
    assert get_db in app.dependency_overrides
    assert next(app.dependency_overrides[get_db]()) is not None


def test_hoy_fijo(cliente, HOY):
    # Las pruebas HTTP no dependen de la fecha real
    assert obtener_hoy in app.dependency_overrides
    assert app.dependency_overrides[obtener_hoy]() == HOY


def test_entorno_de_prueba():
    import os

    assert os.environ["ENV"] == "test"
    assert os.environ["DB_URL"] == "sqlite://"
