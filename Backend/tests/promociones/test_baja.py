from datetime import date, datetime, time

from src.models import Comanda, DetalleComanda, DetalleFactura, Factura

RUTA = "/promociones"


def test_pro_24_baja_de_promocion_sin_uso(cliente, persistir, crear_plato, crear_promocion):
    plato = crear_plato()
    _, promocion_id = persistir(plato, crear_promocion([plato]))
    respuesta = cliente.delete(f"{RUTA}/{promocion_id}")
    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["dado_de_baja"] is True


def test_pro_25_baja_de_promocion_en_uso(
    cliente, sesion, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato]))
    comanda = Comanda(fecha=date(2026, 6, 15), hora=time(12), mozo_id=1, mesa_id=1)
    comanda.detalles.append(DetalleComanda(cantidad=1, producto_id=plato_id))
    factura = Factura(fecha_hora_emision=datetime(2026, 6, 15, 12), comanda=comanda)
    detalle = DetalleFactura(
        precio_unitario=100, cantidad=1, precio_final=90, promocion_id=promocion_id,
        detalle_comanda=comanda.detalles[0],
    )
    factura.detalles.append(detalle)
    sesion.add(factura)
    sesion.commit()
    detalle_id = detalle.id
    sesion.close()

    assert cliente.delete(f"{RUTA}/{promocion_id}").status_code == 204

    detalle = sesion.get(DetalleFactura, detalle_id)
    assert detalle.promocion_id == promocion_id
    assert detalle.precio_final == 90


def test_pro_26_delete_repetido_es_idempotente(
    cliente, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    _, promocion_id = persistir(plato, crear_promocion([plato], dado_de_baja=True))
    assert cliente.delete(f"{RUTA}/{promocion_id}").status_code == 204
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["dado_de_baja"] is True


def test_pro_27_baja_de_id_desconocido(cliente):
    assert cliente.delete(f"{RUTA}/999").status_code == 404


def test_pro_65_baja_de_producto_con_promocion(
    cliente, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato]))
    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 204
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["productos_ids"] == [plato_id]


def test_pro_66_baja_via_put_de_producto_con_promocion(
    cliente, persistir, crear_bebida, crear_promocion
):
    bebida = crear_bebida()
    bebida_id, promocion_id = persistir(bebida, crear_promocion([bebida]))
    respuesta = cliente.put(
        f"/productos/bebidas/{bebida_id}",
        json={
            "nombre": "Cerveza",
            "precio": "800.00",
            "es_alcoholica": True,
            "dado_de_baja": True,
        },
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["productos_ids"] == [bebida_id]
