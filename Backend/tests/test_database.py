import inspect

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src import database


@pytest.fixture
def motor_configurado():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    database.configurar_sqlite(motor)
    with motor.begin() as conexion:
        conexion.execute(text("CREATE TABLE padre (id INTEGER PRIMARY KEY)"))
        conexion.execute(
            text(
                "CREATE TABLE hijo (id INTEGER PRIMARY KEY, "
                "padre_id INTEGER REFERENCES padre(id))"
            )
        )
    yield motor
    motor.dispose()


def test_clave_foranea_inexistente_se_rechaza(motor_configurado):
    sesion = sessionmaker(bind=motor_configurado)()
    with pytest.raises(IntegrityError):
        sesion.execute(text("INSERT INTO hijo (id, padre_id) VALUES (1, 999)"))
        sesion.commit()
    sesion.close()


def test_escritura_confirmada_visible_desde_otra_sesion(motor_configurado):
    fabrica = sessionmaker(bind=motor_configurado)
    escritora = fabrica()
    escritora.execute(text("INSERT INTO padre (id) VALUES (1)"))
    escritora.commit()
    lectora = fabrica()
    assert lectora.execute(text("SELECT COUNT(*) FROM padre")).scalar() == 1
    escritora.close()
    lectora.close()


def test_begin_emite_begin_immediate(motor_configurado):
    sentencias = []

    @event.listens_for(motor_configurado, "before_cursor_execute")
    def capturar(conexion, cursor, sentencia, parametros, contexto, ejecutar_muchos):
        sentencias.append(sentencia)

    with motor_configurado.connect() as conexion:
        conexion.execute(text("SELECT 1"))
    # El listener begin usa exec_driver_sql, que pasa por before_cursor_execute
    assert any(s.strip().upper() == "BEGIN IMMEDIATE" for s in sentencias)


def test_get_db_no_ejecuta_pragma():
    assert "PRAGMA" not in inspect.getsource(database.get_db)
