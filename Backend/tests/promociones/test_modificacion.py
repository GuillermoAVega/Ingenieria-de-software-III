from datetime import date, datetime, time

import pytest

from src.models import Comanda, DetalleComanda, DetalleFactura, Factura

RUTA = "/promociones"


def _cuerpo(productos_ids, **extra):
    return {
        "nombre": "Nuevo nombre",
        "fecha_desde": "2026-06-01",
        "fecha_hasta": "2026-06-30",
        "tipo": "porcentaje",
        "descuento": "20.00",
        **extra,
        "productos_ids": productos_ids,
    }


def _usar(sesion, promocion_id, producto_id):
    """Inserta directamente una línea de factura que referencia la promoción."""
    comanda = Comanda(fecha=date(2026, 6, 15), hora=time(12), mozo_id=1, mesa_id=1)
    comanda.detalles.append(DetalleComanda(cantidad=1, producto_id=producto_id))
    factura = Factura(fecha_hora_emision=datetime(2026, 6, 15, 12), comanda=comanda)
    factura.detalles.append(
        DetalleFactura(
            precio_unitario=100, cantidad=1, precio_final=90,
            promocion_id=promocion_id, activo=False,
            detalle_comanda=comanda.detalles[0],
        )
    )
    sesion.add(factura)
    sesion.commit()
    sesion.close()


@pytest.fixture
def escenario(persistir, crear_plato, crear_bebida, crear_promocion):
    plato, bebida = crear_plato(), crear_bebida()
    promocion = crear_promocion([plato], nombre="Original", descuento="10.00")
    plato_id, bebida_id, promocion_id = persistir(plato, bebida, promocion)
    return plato_id, bebida_id, promocion_id


def _leer(cliente, promocion_id):
    # `en_uso` es derivado del uso en facturas, no un dato modificable
    cuerpo = cliente.get(f"{RUTA}/{promocion_id}").json()
    cuerpo.pop("en_uso")
    return cuerpo


def test_pro_19_modificacion_valida(cliente, escenario):
    plato_id, bebida_id, promocion_id = escenario
    respuesta = cliente.put(
        f"{RUTA}/{promocion_id}", json=_cuerpo([bebida_id, plato_id])
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Nuevo nombre"
    assert float(cuerpo["descuento"]) == 20
    assert cuerpo["productos_ids"] == sorted([plato_id, bebida_id])
    cuerpo.pop("en_uso")
    assert _leer(cliente, promocion_id) == cuerpo


def test_pro_19_los_productos_se_reemplazan(cliente, escenario):
    plato_id, bebida_id, promocion_id = escenario
    respuesta = cliente.put(f"{RUTA}/{promocion_id}", json=_cuerpo([bebida_id]))
    assert respuesta.status_code == 200
    assert respuesta.json()["productos_ids"] == [bebida_id]


def test_pro_20_promocion_en_uso(cliente, sesion, escenario):
    plato_id, _, promocion_id = escenario
    antes = _leer(cliente, promocion_id)
    _usar(sesion, promocion_id, plato_id)
    respuesta = cliente.put(f"{RUTA}/{promocion_id}", json=_cuerpo([plato_id]))
    assert respuesta.status_code == 409
    assert _leer(cliente, promocion_id) == antes


def test_plc_20_cambio_de_tipo_en_uso(cliente, sesion, escenario):
    # PLC-20
    plato_id, _, promocion_id = escenario
    antes = _leer(cliente, promocion_id)
    _usar(sesion, promocion_id, plato_id)
    cuerpo = _cuerpo([plato_id], tipo="lleva_paga", lleva=2, paga=1)
    cuerpo.pop("descuento")
    respuesta = cliente.put(f"{RUTA}/{promocion_id}", json=cuerpo)
    assert respuesta.status_code == 409
    assert _leer(cliente, promocion_id) == antes


def test_pro_70_referenciada_solo_por_una_linea_inactiva(cliente, sesion, escenario):
    # `_usar` crea la línea con activo = False
    plato_id, _, promocion_id = escenario
    _usar(sesion, promocion_id, plato_id)
    respuesta = cliente.put(f"{RUTA}/{promocion_id}", json=_cuerpo([plato_id]))
    assert respuesta.status_code == 409


def test_pro_21_modificacion_invalida(cliente, escenario):
    plato_id, _, promocion_id = escenario
    antes = _leer(cliente, promocion_id)
    respuesta = cliente.put(
        f"{RUTA}/{promocion_id}", json=_cuerpo([plato_id], descuento="0")
    )
    assert respuesta.status_code == 422
    assert _leer(cliente, promocion_id) == antes


def test_pro_22_id_desconocido(cliente, escenario):
    plato_id, _, _ = escenario
    assert cliente.put(f"{RUTA}/999", json=_cuerpo([plato_id])).status_code == 404


def test_pro_23_producto_nuevo_dado_de_baja(cliente, persistir, crear_plato, escenario):
    plato_id, _, promocion_id = escenario
    baja = crear_plato(nombre="Baja")
    baja.dado_de_baja = True
    baja_id = persistir(baja)
    antes = _leer(cliente, promocion_id)
    respuesta = cliente.put(f"{RUTA}/{promocion_id}", json=_cuerpo([plato_id, baja_id]))
    assert respuesta.status_code == 409
    assert _leer(cliente, promocion_id) == antes


def test_pro_69_producto_nuevo_inexistente(cliente, escenario):
    plato_id, _, promocion_id = escenario
    antes = _leer(cliente, promocion_id)
    respuesta = cliente.put(f"{RUTA}/{promocion_id}", json=_cuerpo([plato_id, 999]))
    assert respuesta.status_code == 422
    error = respuesta.json()["detail"][0]
    assert error["type"] == "producto_inexistente"
    assert error["ids"] == [999]
    assert _leer(cliente, promocion_id) == antes


def test_pro_71_productos_conservados_no_se_revalidan(cliente, sesion, escenario):
    from src.productos.models import Producto

    plato_id, _, promocion_id = escenario
    sesion.get(Producto, plato_id).dado_de_baja = True
    sesion.commit()
    sesion.close()
    respuesta = cliente.put(
        f"{RUTA}/{promocion_id}", json=_cuerpo([plato_id], nombre="Renombrada")
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Renombrada"


def test_fecha_hasta_vencida_solo_se_rechaza_si_cambia(
    cliente, persistir, crear_plato, crear_promocion
):
    plato = crear_plato()
    plato_id, promocion_id = persistir(
        plato,
        crear_promocion([plato], desde=date(2026, 5, 1), hasta=date(2026, 5, 31)),
    )
    # Conserva la fecha_hasta vencida: se permite
    conservada = cliente.put(
        f"{RUTA}/{promocion_id}",
        json=_cuerpo([plato_id], fecha_desde="2026-05-01", fecha_hasta="2026-05-31"),
    )
    assert conservada.status_code == 200
    # Cambia a otra fecha vencida: se rechaza
    cambiada = cliente.put(
        f"{RUTA}/{promocion_id}",
        json=_cuerpo([plato_id], fecha_desde="2026-05-01", fecha_hasta="2026-05-30"),
    )
    assert cambiada.status_code == 422
