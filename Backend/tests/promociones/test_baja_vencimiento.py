from datetime import date, timedelta

from sqlalchemy import event

from src.promociones.services import dar_de_baja_vencidas
from tests.conftest import HOY_FIJO

RUTA = "/promociones"
AYER = HOY_FIJO - timedelta(days=1)


def _vencida(persistir, crear_plato, crear_promocion, hasta=AYER, nombre="Plato"):
    plato = crear_plato(nombre=nombre)
    return persistir(crear_promocion([plato], desde=date(2026, 1, 1), hasta=hasta))


def test_plc_13_listado_da_de_baja_las_vencidas(
    cliente, persistir, crear_plato, crear_promocion
):
    _vencida(persistir, crear_plato, crear_promocion)
    assert cliente.get(RUTA).json() == []


def test_plc_14_listado_con_bajas_muestra_la_vencida(
    cliente, persistir, crear_plato, crear_promocion
):
    pid = _vencida(persistir, crear_plato, crear_promocion)
    r = cliente.get(RUTA, params={"incluir_bajas": "true"}).json()
    assert [(p["id"], p["dado_de_baja"]) for p in r] == [(pid, True)]


def test_plc_15_get_por_id_da_de_baja_la_vencida(
    cliente, persistir, crear_plato, crear_promocion
):
    pid = _vencida(persistir, crear_plato, crear_promocion)
    r = cliente.get(f"{RUTA}/{pid}")
    assert r.status_code == 200 and r.json()["dado_de_baja"] is True


def test_plc_16_fecha_hasta_igual_a_hoy_no_se_da_de_baja(
    cliente, persistir, crear_plato, crear_promocion
):
    pid = _vencida(persistir, crear_plato, crear_promocion, hasta=HOY_FIJO)
    assert cliente.get(f"{RUTA}/{pid}").json()["dado_de_baja"] is False


def test_plc_17_sentencia_unica(sesion, persistir, crear_plato, crear_promocion):
    ids = [
        _vencida(persistir, crear_plato, crear_promocion, nombre=f"Plato {n}")
        for n in range(3)
    ]
    sentencias = []

    def registrar(_conn, _cursor, statement, *_args):
        sentencias.append(statement)

    motor = sesion.get_bind()
    event.listen(motor, "before_cursor_execute", registrar)
    try:
        dar_de_baja_vencidas(sesion, HOY_FIJO)
    finally:
        event.remove(motor, "before_cursor_execute", registrar)
    updates = [s for s in sentencias if s.lstrip().upper().startswith("UPDATE")]
    assert len(updates) == 1
    from src.promociones.models import Promocion

    assert all(sesion.get(Promocion, i).dado_de_baja for i in ids)


def test_plc_18_conserva_las_lineas(
    cliente, sesion, persistir, crear_plato, crear_promocion
):
    from datetime import datetime, time

    from src.models import Comanda, DetalleComanda, DetalleFactura, Factura

    plato = crear_plato()
    plato_id, pid = persistir(
        plato, crear_promocion([plato], desde=date(2026, 1, 1), hasta=AYER)
    )
    comanda = Comanda(fecha=HOY_FIJO, hora=time(12), mozo_id=1, mesa_id=1)
    sesion.add(comanda)
    sesion.flush()
    dc = DetalleComanda(comanda_id=comanda.id, producto_id=plato_id, cantidad=1)
    sesion.add(dc)
    sesion.flush()
    factura = Factura(
        comanda_id=comanda.id, fecha_hora_emision=datetime(2026, 6, 14, 13), importe_total=0
    )
    sesion.add(factura)
    sesion.flush()
    linea = DetalleFactura(
        factura_id=factura.id, detalle_comanda_id=dc.id,
        precio_unitario=100.0, cantidad=1, precio_final=90.0, promocion_id=pid,
    )
    sesion.add(linea)
    sesion.commit()
    cuerpo = cliente.get(f"{RUTA}/{pid}").json()
    assert cuerpo["dado_de_baja"] is True and cuerpo["en_uso"] is True
    sesion.refresh(linea)
    assert linea.promocion_id == pid and linea.precio_final == 90.0
