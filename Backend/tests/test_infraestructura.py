from src.database import get_db
from src.main import app


def test_motor_en_memoria(motor):
    # La suite nunca debe tocar el archivo SQLite real
    assert str(motor.url) == "sqlite://"


def test_get_db_sobrescrito(cliente, sesion):
    assert get_db in app.dependency_overrides
    assert next(app.dependency_overrides[get_db]()) is not None


def test_hoy_fijo(HOY):
    # obtener_hoy nace en la tarea 7.1; por ahora solo se verifica la constante
    from datetime import date

    assert isinstance(HOY, date)


def test_entorno_de_prueba():
    import os

    assert os.environ["ENV"] == "test"
    assert os.environ["DB_URL"] == "sqlite://"
