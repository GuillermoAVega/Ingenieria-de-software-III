from datetime import date, datetime, time

from src.models import Comanda, DetalleComanda, DetalleFactura, Factura

RUTA = "/promociones"


def _usar(sesion, plato_id, promocion_id, activo=True):
    comanda = Comanda(fecha=date(2026, 6, 15), hora=time(12), mozo_id=1, mesa_id=1)
    comanda.detalles.append(DetalleComanda(cantidad=1, producto_id=plato_id))
    factura = Factura(fecha_hora_emision=datetime(2026, 6, 15, 12), comanda=comanda)
    factura.detalles.append(
        DetalleFactura(
            precio_unitario=100, cantidad=1, precio_final=90, promocion_id=promocion_id,
            detalle_comanda=comanda.detalles[0], activo=activo,
        )
    )
    sesion.add(factura)
    sesion.commit()
    sesion.close()


def _cuerpo(plato_id):
    return {
        "nombre": "Nueva", "fecha_desde": "2026-01-01", "fecha_hasta": "2999-01-01",
        "tipo": "porcentaje", "descuento": "10", "productos_ids": [plato_id],
    }


def test_pro_75_sin_uso_en_alta_consulta_listado_y_modificacion(
    cliente, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato]))
    alta = cliente.post(RUTA, json=_cuerpo(plato_id))
    assert alta.status_code == 201
    assert alta.json()["en_uso"] is False
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["en_uso"] is False
    assert [p["en_uso"] for p in cliente.get(RUTA).json()] == [False, False]
    modificada = cliente.put(f"{RUTA}/{promocion_id}", json=_cuerpo(plato_id))
    assert modificada.status_code == 200
    assert modificada.json()["en_uso"] is False


def test_pro_76_en_uso_en_consulta_y_listado(
    cliente, sesion, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    plato_id, usada_id, libre_id = persistir(
        plato, crear_promocion([plato]), crear_promocion([plato])
    )
    _usar(sesion, plato_id, usada_id)
    assert cliente.get(f"{RUTA}/{usada_id}").json()["en_uso"] is True
    assert cliente.get(f"{RUTA}/{libre_id}").json()["en_uso"] is False
    por_id = {p["id"]: p["en_uso"] for p in cliente.get(RUTA).json()}
    assert por_id == {usada_id: True, libre_id: False}


def test_pro_76_en_uso_con_linea_inactiva(
    cliente, sesion, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    plato_id, promocion_id = persistir(plato, crear_promocion([plato]))
    _usar(sesion, plato_id, promocion_id, activo=False)
    assert cliente.get(f"{RUTA}/{promocion_id}").json()["en_uso"] is True
    assert cliente.get(RUTA).json()[0]["en_uso"] is True
