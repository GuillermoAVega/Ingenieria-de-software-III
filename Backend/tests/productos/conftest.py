from datetime import date
from decimal import Decimal

import pytest

from src.productos.bebidas.models import Bebida
from src.productos.combos.models import ComboPromocion
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.platos.models import Plato
from src.productos.postres.models import Postre


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
def crear_combo():
    def _crear(
        nombre="Combo", desde=date(2026, 6, 1), hasta=date(2026, 6, 30), **relaciones
    ):
        return ComboPromocion(
            nombre=nombre,
            nombre_normalizado=nombre.strip().casefold(),
            precio=Decimal("3000.00"),
            fecha_desde=desde,
            fecha_hasta=hasta,
            **relaciones,
        )

    return _crear


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
