"""Prueba de humo del script de datos de ejemplo (`scripts/poblar_db.py`)."""

from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from scripts.poblar_db import poblar_base, resumen
from src.database import configurar_sqlite
from src.models import DetalleComanda, DetalleFactura, Factura
from src.productos.models import Producto
from src.productos_menu.models import ProductoMenu
from src.promociones.services import recalcular_producto


@pytest.fixture
def motor_poblado():
    motor = configurar_sqlite(
        create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    )
    ids = poblar_base(motor, hoy=date.today())
    yield motor, ids
    motor.dispose()


def test_cantidades_basicas(motor_poblado):
    motor, _ = motor_poblado
    cuentas = resumen(motor)
    assert cuentas["Sectores"] >= 3
    assert cuentas["Mesas"] >= 8
    assert cuentas["  Platos"] >= 6
    assert cuentas["  Combos"] >= 1
    assert cuentas["Promociones"] == 11
    assert cuentas["Facturas"] >= 1
    assert cuentas["Detalles de factura"] >= 1


def test_menu_del_dia_solo_referencia_menus_del_dia(motor_poblado):
    motor, _ = motor_poblado
    with Session(motor) as sesion:
        tipos = sesion.scalars(
            select(Producto.tipo).join(ProductoMenu, ProductoMenu.menu_del_dia_id == Producto.id)
        ).all()
    assert len(tipos) == 4
    assert set(tipos) == {"menu_del_dia"}


def test_poblar_dos_veces_es_idempotente(motor_poblado):
    motor, _ = motor_poblado
    antes = resumen(motor)
    poblar_base(motor, hoy=date.today())
    assert resumen(motor) == antes


def _lineas_por_producto(sesion):
    por_producto = {}
    for detalle in sesion.scalars(select(DetalleFactura).join(DetalleComanda).order_by(DetalleFactura.id)):
        por_producto.setdefault(detalle.detalle_comanda.producto_id, []).append(detalle)
    return por_producto


def test_factura_usa_la_promocion_de_mayor_ahorro_y_menor_id_en_empate(motor_poblado):
    motor, ids = motor_poblado
    productos, promos = ids["productos"], ids["promociones"]
    with Session(motor) as sesion:
        por_producto = _lineas_por_producto(sesion)

        (napolitana,) = por_producto[productos["napolitana"]]
        assert napolitana.promocion_id == promos["napolitana"]  # 20 % > 10 %
        assert napolitana.unidades_gratis == 0
        assert napolitana.precio_final == pytest.approx(
            napolitana.precio_unitario * napolitana.cantidad * 0.8
        )

        (bife,) = por_producto[productos["bife"]]
        assert bife.promocion_id == promos["bife_a"]  # empate 15 %: menor id

        # La promoción dada de baja y la vencida no se aplican
        assert por_producto[productos["gaseosa"]][0].promocion_id is None
        assert por_producto[productos["ravioles"]][0].promocion_id is None

        for factura in sesion.scalars(select(Factura)):
            assert factura.importe_total == pytest.approx(
                sum(d.precio_final for d in factura.detalles)
            )


def test_facturas_con_lleva_paga_y_competencia_entre_tipos(motor_poblado):
    motor, ids = motor_poblado
    productos, promos = ids["productos"], ids["promociones"]
    with Session(motor) as sesion:
        por_producto = _lineas_por_producto(sesion)

        # 4 empanadas: la 2x1 ahorra 2 unidades (4400) frente al 10 % (880)
        cuatro, una = por_producto[productos["empanada"]]
        assert cuatro.cantidad == 4 and cuatro.promocion_id == promos["empanadas_2x1"]
        assert (cuatro.unidades_gratis, cuatro.precio_final) == (2, pytest.approx(4400))
        # 1 empanada: la 2x1 ahorra 0 y gana el 10 %
        assert una.cantidad == 1 and una.promocion_id == promos["empanadas_10"]
        assert (una.unidades_gratis, una.precio_final) == (0, pytest.approx(1980))

        # 3x2 sobre 3 limonadas: una gratis
        (limonada,) = por_producto[productos["limonada"]][:1]
        assert limonada.promocion_id == promos["limonada_3x2"]
        assert (limonada.cantidad, limonada.unidades_gratis) == (3, 1)
        assert limonada.precio_final == pytest.approx(7000)


def test_recalcular_producto_es_idempotente_sobre_los_datos_poblados(motor_poblado):
    motor, _ = motor_poblado
    with Session(motor) as sesion:
        antes = {
            d.id: (d.promocion_id, d.precio_final, d.unidades_gratis)
            for d in sesion.scalars(select(DetalleFactura))
        }
        for factura in sesion.scalars(select(Factura)):
            for producto_id in {d.detalle_comanda.producto_id for d in factura.detalles}:
                recalcular_producto(sesion, factura, producto_id)
        sesion.flush()
        despues = {
            d.id: (d.promocion_id, d.precio_final, d.unidades_gratis)
            for d in sesion.scalars(select(DetalleFactura))
        }
        assert antes and despues == antes
