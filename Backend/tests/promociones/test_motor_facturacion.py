"""Integración del motor agrupado: POST/PUT/DELETE de líneas de factura (PLC-24..53, PRO-33..55)."""

from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.models import DetalleComanda, Factura
from src.productos.models import Producto
from src.promociones.models import Promocion
from tests.promociones.ayudas import RUTA, post, total


def dos_x_uno(promocionar, ids, **kwargs):
    return promocionar(ids, tipo="lleva_paga", lleva=2, paga=1, descuento=None, **kwargs)


def tres_x_dos(promocionar, ids, **kwargs):
    return promocionar(ids, tipo="lleva_paga", lleva=3, paga=2, descuento=None, **kwargs)


def linea(cliente, id_):
    return cliente.get(f"{RUTA}/{id_}").json()


def cambiar_precio(sesion, producto_id, precio):
    sesion.get(Producto, producto_id).precio = Decimal(precio)
    sesion.commit()
    sesion.close()


# ---- Alta: lleva_paga ---------------------------------------------------------


def test_plc_24_2x1_con_una_sola_linea(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = dos_x_uno(promocionar, esc["productos"])
    cuerpo = post(cliente, esc, cantidad=2).json()
    assert (cuerpo["unidades_gratis"], cuerpo["precio_final"], cuerpo["promocion_id"]) == (
        1,
        100,
        promo,
    )
    assert total(cliente, esc["factura_id"]) == 100


@pytest.mark.parametrize(
    "cantidad, gratis, final, aplicada",
    [(3, 1, 200, True), (2, 0, 200, False), (7, 2, 500, True)],
    ids=["plc25", "plc26", "plc27"],
)
def test_plc_25_26_27_3x2(cliente, armar, promocionar, cantidad, gratis, final, aplicada):
    esc = armar(("100.00",))
    promo = tres_x_dos(promocionar, esc["productos"])
    cuerpo = post(cliente, esc, cantidad=cantidad).json()
    assert cuerpo["unidades_gratis"] == gratis
    assert cuerpo["precio_final"] == final
    assert cuerpo["promocion_id"] == (promo if aplicada else None)


def test_plc_28_44_varias_lineas_del_mismo_producto_suman(cliente, armar, promocionar):
    # PLC-44
    esc = armar(("100.00",))
    promo = dos_x_uno(promocionar, esc["productos"])
    primera = post(cliente, esc).json()
    assert primera["unidades_gratis"] == 0
    assert total(cliente, esc["factura_id"]) == 100
    segunda = post(cliente, esc).json()
    # Se recalcularon ambas: empate de precio -> la unidad gratis es de la línea de menor id
    assert linea(cliente, primera["id"])["unidades_gratis"] == 1
    assert linea(cliente, primera["id"])["precio_final"] == 0
    assert linea(cliente, primera["id"])["promocion_id"] == promo
    assert segunda["unidades_gratis"] == 0 and segunda["promocion_id"] is None
    assert total(cliente, esc["factura_id"]) == 100


def test_plc_29_gratis_a_la_linea_mas_barata(cliente, armar, promocionar, sesion):
    esc = armar(("100.00",))
    promo = dos_x_uno(promocionar, esc["productos"])
    cara = post(cliente, esc).json()
    cambiar_precio(sesion, esc["productos"][0], "80.00")
    barata = post(cliente, esc).json()
    cara, barata = linea(cliente, cara["id"]), linea(cliente, barata["id"])
    assert (barata["unidades_gratis"], barata["precio_final"], barata["promocion_id"]) == (1, 0, promo)
    assert (cara["unidades_gratis"], cara["precio_final"], cara["promocion_id"]) == (0, 100, None)


def test_plc_32_productos_distintos_no_se_combinan(cliente, armar, promocionar):
    esc = armar(("100.00", "100.00"))
    dos_x_uno(promocionar, esc["productos"])
    a = post(cliente, esc, indice=0).json()
    b = post(cliente, esc, indice=1).json()
    assert (a["unidades_gratis"], b["unidades_gratis"]) == (0, 0)
    assert total(cliente, esc["factura_id"]) == 200


# ---- Competencia entre tipos ----------------------------------------------------


def test_plc_33_lleva_paga_supera_al_porcentaje(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], descuento="30.00")
    x2 = dos_x_uno(promocionar, esc["productos"])
    cuerpo = post(cliente, esc, cantidad=2).json()
    assert (cuerpo["promocion_id"], cuerpo["precio_final"]) == (x2, 100)


def test_plc_34_porcentaje_supera_a_lleva_paga(cliente, armar, promocionar):
    esc = armar(("100.00",))
    pct = promocionar(esc["productos"], descuento="60.00")
    dos_x_uno(promocionar, esc["productos"])
    cuerpo = post(cliente, esc, cantidad=2).json()
    assert (cuerpo["promocion_id"], cuerpo["precio_final"], cuerpo["unidades_gratis"]) == (
        pct,
        80,
        0,
    )


@pytest.mark.parametrize("porcentaje_primero", [True, False])
def test_plc_35_empate_de_ahorro_gana_menor_id(cliente, armar, promocionar, porcentaje_primero):
    esc = armar(("100.00",))
    if porcentaje_primero:
        primera = promocionar(esc["productos"], descuento="50.00")
        dos_x_uno(promocionar, esc["productos"])
    else:
        primera = dos_x_uno(promocionar, esc["productos"])
        promocionar(esc["productos"], descuento="50.00")
    assert post(cliente, esc, cantidad=2).json()["promocion_id"] == primera


def test_plc_37_39_porcentaje_ganador_en_todas_las_lineas(cliente, armar, promocionar):
    esc = armar(("100.00",))
    ganadora = promocionar(esc["productos"], descuento="40.00")
    dos_x_uno(promocionar, esc["productos"])
    a, b, c = (post(cliente, esc).json() for _ in range(3))
    lineas = [linea(cliente, x["id"]) for x in (a, b, c)]
    # 3 unidades: la 2x1 ahorra 100 (una gratis) y el 40 % ahorra 120: gana el porcentaje
    assert [l["promocion_id"] for l in lineas] == [ganadora] * 3
    assert [l["unidades_gratis"] for l in lineas] == [0, 0, 0]
    assert total(cliente, esc["factura_id"]) == 180


def test_plc_38_linea_sin_unidades_gratis_queda_sin_promocion(cliente, armar, promocionar):
    esc = armar(("100.00",))
    dos_x_uno(promocionar, esc["productos"])
    a, b = post(cliente, esc).json(), post(cliente, esc).json()
    otra = linea(cliente, b["id"])
    assert (otra["promocion_id"], otra["unidades_gratis"], otra["precio_final"]) == (None, 0, 100)
    assert linea(cliente, a["id"])["promocion_id"] is not None


# ---- Promociones conservadas ----------------------------------------------------


def test_plc_41_promocion_conservada_tras_su_baja(cliente, armar, promocionar):
    esc = armar(("100.00",))
    x2 = dos_x_uno(promocionar, esc["productos"])
    promocionar(esc["productos"], descuento="10.00")
    primera = post(cliente, esc, cantidad=2).json()
    assert primera["promocion_id"] == x2
    assert cliente.delete(f"/promociones/{x2}").status_code == 204
    segunda = post(cliente, esc, cantidad=2).json()
    # La dada de baja sigue compitiendo: 2 unidades gratis (200) frente al 10 % (40)
    primera = linea(cliente, primera["id"])
    assert (primera["promocion_id"], primera["unidades_gratis"]) == (x2, 2)
    assert (segunda["promocion_id"], segunda["unidades_gratis"]) == (None, 0)
    assert total(cliente, esc["factura_id"]) == 200


def test_plc_42_promocion_conservada_no_se_revalida(cliente, armar, promocionar, sesion):
    esc = armar(("100.00",))
    promo = dos_x_uno(promocionar, esc["productos"])
    primera = post(cliente, esc, cantidad=2).json()
    vieja = sesion.get(Promocion, promo)
    vieja.fecha_desde, vieja.fecha_hasta = date(2026, 5, 1), date(2026, 5, 31)
    sesion.commit()
    sesion.close()
    r = cliente.put(f"{RUTA}/{primera['id']}", json={"cantidad": 4}).json()
    assert (r["promocion_id"], r["unidades_gratis"], r["precio_final"]) == (promo, 2, 200)


def test_plc_43_la_baja_automatica_precede_al_calculo(cliente, armar, promocionar, sesion):
    # Vencida a HOY_FIJO (2026-06-15) pero vigente a la emisión
    esc = armar(("100.00",), emision=datetime(2026, 6, 5, 12, 0))
    promo = promocionar(
        esc["productos"], desde=date(2026, 6, 1), hasta=date(2026, 6, 10), descuento="50.00"
    )
    cuerpo = post(cliente, esc).json()
    assert (cuerpo["promocion_id"], cuerpo["precio_final"]) == (None, 100)
    assert sesion.get(Promocion, promo).dado_de_baja is True


@pytest.mark.parametrize("metodo", ["put", "delete"])
def test_baja_automatica_tambien_en_put_y_delete(cliente, armar, promocionar, sesion, metodo):
    esc = armar(("100.00",), emision=datetime(2026, 6, 5, 12, 0))
    primera = post(cliente, esc).json()
    promo = promocionar(
        esc["productos"], desde=date(2026, 6, 1), hasta=date(2026, 6, 10), descuento="50.00"
    )
    assert sesion.get(Promocion, promo).dado_de_baja is False
    sesion.close()
    if metodo == "put":
        r = cliente.put(f"{RUTA}/{primera['id']}", json={"cantidad": 2}).json()
        assert (r["promocion_id"], r["precio_final"]) == (None, 200)
    else:
        assert cliente.delete(f"{RUTA}/{primera['id']}").status_code == 204
    assert sesion.get(Promocion, promo).dado_de_baja is True


# ---- Baja de línea ---------------------------------------------------------------


def test_plc_45_baja_de_linea_recalcula_el_grupo(cliente, armar, promocionar):
    esc = armar(("100.00",))
    dos_x_uno(promocionar, esc["productos"])
    a, b = post(cliente, esc).json(), post(cliente, esc).json()
    assert total(cliente, esc["factura_id"]) == 100
    assert cliente.delete(f"{RUTA}/{b['id']}").status_code == 204
    restante = linea(cliente, a["id"])
    assert (restante["unidades_gratis"], restante["promocion_id"], restante["precio_final"]) == (
        0,
        None,
        100,
    )
    assert total(cliente, esc["factura_id"]) == 100


def test_pro_55_total_tras_eliminar_con_bonificacion_en_la_otra_linea(cliente, armar, promocionar):
    esc = armar(("100.00",))
    dos_x_uno(promocionar, esc["productos"])
    a, b = post(cliente, esc).json(), post(cliente, esc).json()
    # a tiene la unidad gratis (menor id); al eliminar a, b queda a precio completo
    assert cliente.delete(f"{RUTA}/{a['id']}").status_code == 204
    assert linea(cliente, b["id"])["precio_final"] == 100
    assert total(cliente, esc["factura_id"]) == 100


def test_plc_46_linea_dada_de_baja_conserva_sus_datos(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = dos_x_uno(promocionar, esc["productos"])
    a, b = post(cliente, esc).json(), post(cliente, esc).json()
    assert cliente.delete(f"{RUTA}/{a['id']}").status_code == 204
    inactivas = cliente.get(RUTA, params={"activo": False, "factura_id": esc["factura_id"]}).json()
    assert len(inactivas) == 1
    assert (
        inactivas[0]["id"],
        inactivas[0]["promocion_id"],
        inactivas[0]["precio_final"],
        inactivas[0]["unidades_gratis"],
    ) == (a["id"], promo, 0, 1)


# ---- PUT con cambio de detalle_comanda_id -------------------------------------------


def test_plc_47_cambio_de_detalle_recalcula_ambos_grupos(cliente, armar, promocionar):
    esc = armar(("100.00", "60.00"))
    dos_x_uno(promocionar, esc["productos"])
    a1, a2 = post(cliente, esc, indice=0).json(), post(cliente, esc, indice=0).json()
    b1 = post(cliente, esc, indice=1).json()
    assert linea(cliente, a1["id"])["unidades_gratis"] == 1
    r = cliente.put(f"{RUTA}/{a1['id']}", json={"detalle_comanda_id": esc["detalles"][1]}).json()
    assert (r["precio_unitario"], r["unidades_gratis"], r["precio_final"]) == (60, 1, 0)
    assert linea(cliente, a2["id"])["unidades_gratis"] == 0
    assert linea(cliente, b1["id"])["unidades_gratis"] == 0
    assert total(cliente, esc["factura_id"]) == 160


def test_plc_48_cambio_de_detalle_al_mismo_producto(cliente, armar, promocionar, sesion):
    esc = armar(("100.00",))
    dos_x_uno(promocionar, esc["productos"])
    sesion.add(DetalleComanda(comanda_id=esc["comanda_id"], producto_id=esc["productos"][0], cantidad=1))
    sesion.commit()
    otro_dc = max(
        sesion.scalars(
            select(DetalleComanda.id).where(DetalleComanda.comanda_id == esc["comanda_id"])
        )
    )
    sesion.close()
    a, b = post(cliente, esc).json(), post(cliente, esc).json()
    r = cliente.put(f"{RUTA}/{b['id']}", json={"detalle_comanda_id": otro_dc}).json()
    assert r["detalle_comanda_id"] == otro_dc
    gratis = [linea(cliente, x["id"])["unidades_gratis"] for x in (a, b)]
    assert gratis == [1, 0]
    assert total(cliente, esc["factura_id"]) == 100


def test_plc_53_cambio_de_cantidad_en_lleva_paga(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = tres_x_dos(promocionar, esc["productos"])
    a = post(cliente, esc, cantidad=2).json()
    assert (a["unidades_gratis"], a["promocion_id"]) == (0, None)
    r = cliente.put(f"{RUTA}/{a['id']}", json={"cantidad": 3}).json()
    assert (r["unidades_gratis"], r["promocion_id"], r["precio_final"]) == (1, promo, 200)


# ---- Combo y respuesta ------------------------------------------------------------------


def test_plc_49_combo_con_lleva_paga(
    cliente, sesion, persistir, crear_plato, crear_combo, crear_comanda_facturable, promocionar
):
    plato = persistir(crear_plato(nombre="Componente"))
    combo = crear_combo(platos=[sesion.get(Producto, plato)])
    combo.precio = Decimal("500.00")
    combo_id = persistir(combo)
    comanda_id = persistir(crear_comanda_facturable([combo_id], cantidad=2))
    factura_id = persistir(Factura(fecha_hora_emision=datetime(2026, 6, 15, 13, 0), comanda_id=comanda_id))
    dc = sesion.scalars(
        select(DetalleComanda.id).where(DetalleComanda.comanda_id == comanda_id)
    ).one()
    sesion.close()
    promo = dos_x_uno(promocionar, [combo_id])
    cuerpo = cliente.post(
        RUTA, json={"factura_id": factura_id, "detalle_comanda_id": dc, "cantidad": 2}
    ).json()
    assert (cuerpo["precio_unitario"], cuerpo["unidades_gratis"], cuerpo["precio_final"]) == (
        500,
        1,
        500,
    )
    assert cuerpo["promocion_id"] == promo


def test_plc_50_calculo_exacto_en_decimal(cliente, armar, promocionar):
    esc = armar(("33.33",))
    tres_x_dos(promocionar, esc["productos"])
    assert post(cliente, esc, cantidad=3).json()["precio_final"] == 66.66


def test_plc_51_respuesta_incluye_unidades_gratis(cliente, armar):
    esc = armar(("100.00",))
    creada = post(cliente, esc).json()
    assert creada["unidades_gratis"] == 0
    assert linea(cliente, creada["id"])["unidades_gratis"] == 0
    assert cliente.get(RUTA).json()[0]["unidades_gratis"] == 0


def test_plc_52_unidades_gratis_del_cliente_se_ignora(cliente, armar):
    esc = armar(("100.00",))
    creada = post(cliente, esc, unidades_gratis=5).json()
    assert creada["unidades_gratis"] == 0
    r = cliente.put(f"{RUTA}/{creada['id']}", json={"cantidad": 2, "unidades_gratis": 5}).json()
    assert (r["unidades_gratis"], r["precio_final"]) == (0, 200)


# ---- Detección (PRO-33..40) ----------------------------------------------------------------


def test_pro_34_una_promocion_vigente(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promo = promocionar(esc["productos"], descuento="10.00")
    assert post(cliente, esc).json()["promocion_id"] == promo


def test_pro_35_mayor_ahorro_gana(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], descuento="10.00")
    mayor = promocionar(esc["productos"], descuento="25.00")
    cuerpo = post(cliente, esc).json()
    assert (cuerpo["promocion_id"], cuerpo["precio_final"]) == (mayor, 75)


def test_pro_36_empate_menor_id(cliente, armar, promocionar):
    esc = armar(("100.00",))
    primera = promocionar(esc["productos"], descuento="20.00")
    promocionar(esc["productos"], descuento="20.00")
    assert post(cliente, esc).json()["promocion_id"] == primera


def test_pro_37_limites_inclusivos(cliente, armar, promocionar):
    esc = armar(("100.00",))
    desde = promocionar(esc["productos"], desde=date(2026, 6, 15), hasta=date(2026, 6, 30))
    assert post(cliente, esc).json()["promocion_id"] == desde
    esc = armar(("100.00",))
    hasta = promocionar(esc["productos"], desde=date(2026, 6, 1), hasta=date(2026, 6, 15))
    assert post(cliente, esc).json()["promocion_id"] == hasta


def test_pro_38_fuera_de_vigencia_a_la_emision(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], desde=date(2026, 6, 16), hasta=date(2026, 6, 30))
    promocionar(esc["productos"], desde=date(2026, 6, 1), hasta=date(2026, 6, 14))
    assert post(cliente, esc).json()["promocion_id"] is None


def test_pro_39_promocion_dada_de_baja(cliente, armar, promocionar):
    esc = armar(("100.00",))
    promocionar(esc["productos"], dado_de_baja=True)
    assert post(cliente, esc).json()["promocion_id"] is None


def test_pro_40_promocion_de_otro_producto(cliente, armar, promocionar):
    esc = armar(("100.00", "100.00"))
    promocionar([esc["productos"][1]])
    assert post(cliente, esc, indice=0).json()["promocion_id"] is None
