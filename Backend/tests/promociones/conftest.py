import itertools

import pytest
from sqlalchemy import select

from src.models import DetalleComanda, Factura
from tests.promociones.ayudas import EMISION


@pytest.fixture
def armar(sesion, persistir, crear_plato, crear_bebida, crear_comanda_facturable):
    """Producto(s) + comanda con una línea por producto + factura emitida en EMISION."""

    llamadas = itertools.count()

    def _armar(precios=("100.00",), emision=EMISION, cantidad=1):
        n = next(llamadas)
        productos = []
        for i, precio in enumerate(precios):
            productos.append(
                crear_plato(nombre=f"Plato {n}-{i}", precio=precio)
                if i % 2 == 0
                else crear_bebida(nombre=f"Bebida {n}-{i}", precio=precio)
            )
        producto_ids = persistir(*productos)
        producto_ids = [producto_ids] if isinstance(producto_ids, int) else producto_ids
        comanda_id = persistir(crear_comanda_facturable(producto_ids, cantidad=cantidad))
        factura_id = persistir(Factura(fecha_hora_emision=emision, comanda_id=comanda_id))
        detalles = sesion.scalars(
            select(DetalleComanda.id)
            .where(DetalleComanda.comanda_id == comanda_id)
            .order_by(DetalleComanda.id)
        ).all()
        sesion.close()
        return {
            "productos": producto_ids,
            "factura_id": factura_id,
            "detalles": list(detalles),
            "comanda_id": comanda_id,
        }

    return _armar


@pytest.fixture
def promocionar(persistir, sesion, crear_promocion):
    def _promocionar(producto_ids, **kwargs):
        from src.productos.models import Producto

        productos = [sesion.get(Producto, i) for i in producto_ids]
        promocion = crear_promocion(productos, **kwargs)
        return persistir(promocion)

    return _promocionar
