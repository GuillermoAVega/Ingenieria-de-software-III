"""Unidad del motor agrupado: `calcular_grupo` es una función pura (sin base de datos)."""

from decimal import Decimal

from src.promociones.services import Asignacion, Candidata, LineaGrupo, calcular_grupo


def linea(id, precio, cantidad=1):
    return LineaGrupo(id=id, precio_unitario=Decimal(precio), cantidad=cantidad)


def lleva_paga(id, lleva, paga):
    return Candidata(id=id, tipo="lleva_paga", descuento=None, lleva=lleva, paga=paga)


def porcentaje(id, descuento):
    return Candidata(id=id, tipo="porcentaje", descuento=Decimal(descuento), lleva=None, paga=None)


def asignacion(promocion_id, precio_final, gratis):
    return Asignacion(promocion_id=promocion_id, precio_final=Decimal(precio_final), unidades_gratis=gratis)


# PLC-24
def test_plc_24_2x1_una_linea():
    r = calcular_grupo([linea(1, "100.00", 2)], [lleva_paga(7, 2, 1)])
    assert r == {1: asignacion(7, "100.00", 1)}


# PLC-25 / PLC-27 triangulan el múltiplo
def test_plc_25_3x2_con_tres():
    r = calcular_grupo([linea(1, "100.00", 3)], [lleva_paga(7, 3, 2)])
    assert r == {1: asignacion(7, "200.00", 1)}


def test_plc_27_multiplos_de_lleva():
    r = calcular_grupo([linea(1, "100.00", 7)], [lleva_paga(7, 3, 2)])
    assert r == {1: asignacion(7, "500.00", 2)}


# PLC-26 y PLC-36
def test_plc_26_36_menos_unidades_que_lleva_no_gana():
    r = calcular_grupo([linea(1, "100.00", 2)], [lleva_paga(7, 3, 2)])
    assert r == {1: asignacion(None, "200.00", 0)}


def test_sin_candidatas_sin_promocion():
    r = calcular_grupo([linea(1, "10.50", 3)], [])
    assert r == {1: asignacion(None, "31.50", 0)}


# PLC-29: la unidad gratis va a la línea más barata
def test_plc_29_gratis_a_la_linea_mas_barata():
    r = calcular_grupo([linea(1, "100.00"), linea(2, "80.00")], [lleva_paga(7, 2, 1)])
    assert r == {1: asignacion(None, "100.00", 0), 2: asignacion(7, "0.00", 1)}


# PLC-30: empate de precio -> menor id (sin importar el orden de entrada)
def test_plc_30_empate_de_precio_menor_id():
    r = calcular_grupo([linea(5, "100.00"), linea(3, "100.00")], [lleva_paga(7, 2, 1)])
    assert r[3] == asignacion(7, "0.00", 1)
    assert r[5] == asignacion(None, "100.00", 0)


# PLC-31: gratis repartidas entre líneas (3x1 con 3 unidades)
def test_plc_31_gratis_repartidas():
    r = calcular_grupo([linea(1, "50.00", 1), linea(2, "100.00", 2)], [lleva_paga(7, 3, 1)])
    assert r == {1: asignacion(7, "0.00", 1), 2: asignacion(7, "100.00", 1)}


# PLC-33 / PLC-34: gana el mayor ahorro en pesos entre tipos
def test_plc_33_lleva_paga_supera_a_porcentaje():
    r = calcular_grupo(
        [linea(1, "100.00", 2)], [porcentaje(1, "30.00"), lleva_paga(2, 2, 1)]
    )
    assert r == {1: asignacion(2, "100.00", 1)}


def test_plc_34_porcentaje_supera_a_lleva_paga():
    r = calcular_grupo(
        [linea(1, "100.00", 2)], [porcentaje(1, "60.00"), lleva_paga(2, 2, 1)]
    )
    assert r == {1: asignacion(1, "80.00", 0)}


# PLC-35: empate de ahorro (50 % sobre 2 x 100 = 100 = 2x1) -> menor id
def test_plc_35_empate_gana_menor_id():
    candidatas = [porcentaje(9, "50.00"), lleva_paga(4, 2, 1)]
    assert calcular_grupo([linea(1, "100.00", 2)], candidatas)[1].promocion_id == 4
    candidatas = [porcentaje(3, "50.00"), lleva_paga(8, 2, 1)]
    assert calcular_grupo([linea(1, "100.00", 2)], candidatas)[1].promocion_id == 3


# PLC-39: porcentaje, todas las líneas reciben la promoción
def test_plc_39_porcentaje_todas_las_lineas():
    r = calcular_grupo([linea(1, "100.00", 1), linea(2, "40.00", 2)], [porcentaje(5, "10.00")])
    assert r == {1: asignacion(5, "90.00", 0), 2: asignacion(5, "72.00", 0)}


# PLC-40: precios distintos
def test_plc_40_precios_distintos_gratis_a_la_de_100():
    r = calcular_grupo([linea(1, "120.00"), linea(2, "100.00")], [lleva_paga(7, 2, 1)])
    assert r[2] == asignacion(7, "0.00", 1)
    assert r[1] == asignacion(None, "120.00", 0)


# PLC-50: Decimal exacto
def test_plc_50_calculo_exacto_en_decimal():
    r = calcular_grupo([linea(1, "33.33", 3)], [lleva_paga(7, 3, 2)])
    assert r[1].precio_final == Decimal("66.66")
    assert r[1].unidades_gratis == 1


def test_ahorro_cero_no_gana_aunque_sea_la_unica_candidata():
    # 100 % sobre precio 0.00: ahorro 0
    r = calcular_grupo([linea(1, "0.00", 2)], [porcentaje(1, "100.00")])
    assert r == {1: asignacion(None, "0.00", 0)}
