from sqlalchemy import create_engine, inspect, text

from src.database import migrar_unidades_gratis_detalle_factura


def test_agrega_unidades_gratis_a_base_legacy_y_es_idempotente():
    motor = create_engine("sqlite://")
    with motor.begin() as conexion:
        conexion.execute(text(
            "CREATE TABLE detalle_factura (id INTEGER PRIMARY KEY, precio_final FLOAT)"
        ))
        conexion.execute(text("INSERT INTO detalle_factura (id, precio_final) VALUES (1, 10)"))

    migrar_unidades_gratis_detalle_factura(motor)
    migrar_unidades_gratis_detalle_factura(motor)  # segunda corrida: no falla

    columnas = {c["name"] for c in inspect(motor).get_columns("detalle_factura")}
    assert "unidades_gratis" in columnas
    with motor.connect() as conexion:
        assert conexion.execute(text("SELECT unidades_gratis FROM detalle_factura")).scalar() == 0


def test_sin_tabla_detalle_factura_no_hace_nada():
    migrar_unidades_gratis_detalle_factura(create_engine("sqlite://"))
