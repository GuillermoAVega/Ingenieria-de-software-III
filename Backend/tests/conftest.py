import itertools
import os
from datetime import date, timedelta
from decimal import Decimal

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
from src.productos.bebidas.models import Bebida
from src.productos.combos.models import (
    ComboBebida,
    ComboPlato,
    ComboPostre,
    ComboPromocion,
)
from src.productos.menus_del_dia.models import MenuDelDia
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.platos.models import Plato
from src.productos.postres.models import Postre
from src.productos_menu.models import ProductoMenu
from src.productos.services import obtener_hoy
from src.secciones.models import Seccion

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


@pytest.fixture
def persistir(sesion):
    """Guarda objetos ORM y cierra la sesión de prueba; devuelve sus ids.

    El motor de pruebas comparte una única conexión: la sesión del test no debe
    dejar una transacción abierta mientras el cliente HTTP atiende la petición.
    """

    def _persistir(*objetos):
        sesion.add_all(objetos)
        sesion.flush()
        ids = [objeto.id for objeto in objetos]
        sesion.commit()
        sesion.close()
        return ids[0] if len(ids) == 1 else ids

    return _persistir


@pytest.fixture
def crear_seccion():
    # Autoasignadas desde 1001 para no chocar con las posiciones explícitas de las pruebas
    posiciones = itertools.count(1001)

    def _crear(nombre="Entradas", subtitulo=None, posicion=None):
        return Seccion(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            subtitulo=subtitulo,
            posicion=next(posiciones) if posicion is None else posicion,
        )

    return _crear


@pytest.fixture
def crear_plato():
    def _crear(nombre="Milanesa", precio="1500.00", cant_personas=2, **extra):
        return Plato(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal(precio),
            cant_personas=cant_personas,
            **extra,
        )

    return _crear


@pytest.fixture
def crear_bebida():
    def _crear(nombre="Cerveza", precio="800.00", es_alcoholica=True):
        return Bebida(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal(precio),
            es_alcoholica=es_alcoholica,
        )

    return _crear


@pytest.fixture
def crear_postre():
    def _crear(nombre="Flan", precio="600.00"):
        return Postre(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal(precio),
        )

    return _crear


@pytest.fixture
def crear_menu():
    def _crear(plato, postre, nombre="Menú del día", precio="2000.00"):
        return MenuEjecutivo(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal(precio),
            plato=plato,
            postre=postre,
        )

    return _crear


@pytest.fixture
def crear_menu_del_dia():
    def _crear(nombre="Menú del lunes", precio="2500.00", **extra):
        return MenuDelDia(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal(precio),
            **extra,
        )

    return _crear


@pytest.fixture
def crear_combo():
    def _crear(
        nombre="Combo", desde=date(2026, 6, 1), hasta=date(2026, 6, 30), **relaciones
    ):
        # `platos=[plato]` o `[(plato, cantidad)]` (cantidad 1 por defecto)
        def asociaciones(clase, atributo, componentes):
            pares = [c if isinstance(c, tuple) else (c, 1) for c in componentes]
            return [clase(**{atributo: c}, cantidad=n) for c, n in pares]

        return ComboPromocion(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal("3000.00"),
            fecha_desde=desde,
            fecha_hasta=hasta,
            componentes_platos=asociaciones(ComboPlato, "plato", relaciones.pop("platos", [])),
            componentes_bebidas=asociaciones(ComboBebida, "bebida", relaciones.pop("bebidas", [])),
            componentes_postres=asociaciones(ComboPostre, "postre", relaciones.pop("postres", [])),
            **relaciones,
        )

    return _crear


@pytest.fixture
def crear_producto_menu():
    # Autoasignadas desde 2100-01-01 para no chocar con las fechas explícitas de las pruebas
    dias = itertools.count()

    def _crear(menu_del_dia, fecha=None):
        if fecha is None:
            fecha = date(2100, 1, 1) + timedelta(days=next(dias))
        return ProductoMenu(menu_del_dia=menu_del_dia, fecha=fecha)

    return _crear


@pytest.fixture
def crear_promocion():
    def _crear(
        productos,
        nombre="Promo",
        desde=date(2026, 6, 1),
        hasta=date(2026, 6, 30),
        descuento="10.00",
        dado_de_baja=False,
        tipo="porcentaje",
        lleva=None,
        paga=None,
    ):
        # Importación diferida: el fixture solo se usa en pruebas de promociones
        from src.promociones.models import Promocion

        return Promocion(
            nombre=nombre,
            fecha_desde=desde,
            fecha_hasta=hasta,
            tipo=tipo,
            descuento=None if descuento is None else Decimal(descuento),
            lleva=lleva,
            paga=paga,
            dado_de_baja=dado_de_baja,
            productos=list(productos),
        )

    return _crear


@pytest.fixture
def crear_comanda_facturable():
    """Comanda con una línea por producto persistido, lista para facturar."""

    def _crear(producto_ids, cantidad=1):
        from datetime import time

        from src.models import Comanda, DetalleComanda

        comanda = Comanda(fecha=HOY_FIJO, hora=time(12), mozo_id=1, mesa_id=1)
        comanda.detalles = [
            DetalleComanda(cantidad=cantidad, producto_id=producto_id)
            for producto_id in producto_ids
        ]
        return comanda

    return _crear
