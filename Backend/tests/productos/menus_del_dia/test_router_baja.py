"""Baja de MenuDelDia por HTTP: las fechas `> hoy` se borran físicamente."""
from datetime import date

from sqlalchemy import select

from src.productos.menus_del_dia.models import MenuDelDia
from src.productos_menu.models import ProductoMenu

PREFIJO = "/productos/menus-del-dia"
HOY = date(2026, 6, 15)  # fecha fijada por el fixture `cliente`
AYER = date(2026, 6, 14)
MANANA = date(2026, 6, 16)


def _cuerpo_put(**cambios):
    return {"nombre": "Menú del lunes", "precio": "2500.00", "dado_de_baja": True, **cambios}


def _filas(sesion):
    filas = set(sesion.execute(select(ProductoMenu.id, ProductoMenu.fecha)).all())
    sesion.rollback()
    return filas


def _menu(crear_menu_del_dia, crear_producto_menu, persistir, *fechas):
    menu = crear_menu_del_dia()
    ids = persistir(menu, *(crear_producto_menu(menu, f) for f in fechas))
    return (ids, []) if not fechas else (ids[0], ids[1:])


def test_delete_con_fechas_futuras_responde_204_y_las_borra(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    menu_id, registros = _menu(crear_menu_del_dia, crear_producto_menu, persistir, AYER, HOY, MANANA)

    respuesta = cliente.delete(f"{PREFIJO}/{menu_id}")

    assert respuesta.status_code == 204
    assert _filas(sesion) == {(registros[0], AYER), (registros[1], HOY)}
    assert sesion.get(MenuDelDia, menu_id).dado_de_baja is True


def test_put_con_dado_de_baja_true_responde_200_y_borra_las_fechas_futuras(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    menu_id, _ = _menu(crear_menu_del_dia, crear_producto_menu, persistir, MANANA)

    respuesta = cliente.put(f"{PREFIJO}/{menu_id}", json=_cuerpo_put())

    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True
    assert _filas(sesion) == set()


def test_mdd_52_solo_fechas_pasadas_responde_204_y_conserva_los_registros(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    menu_id, registros = _menu(crear_menu_del_dia, crear_producto_menu, persistir, AYER)

    respuesta = cliente.delete(f"{PREFIJO}/{menu_id}")

    assert respuesta.status_code == 204
    assert _filas(sesion) == {(registros[0], AYER)}


def test_mdd_53_sin_fechas_responde_204_por_delete_y_200_por_put(
    cliente, crear_menu_del_dia, persistir
):
    uno = persistir(crear_menu_del_dia())
    otro = persistir(crear_menu_del_dia(nombre="Otro"))

    assert cliente.delete(f"{PREFIJO}/{uno}").status_code == 204
    respuesta = cliente.put(f"{PREFIJO}/{otro}", json=_cuerpo_put(nombre="Otro"))
    assert respuesta.status_code == 200
    assert respuesta.json()["dado_de_baja"] is True


def test_mdd_57_delete_repetido_responde_204_sin_cuerpo(cliente, crear_menu_del_dia, persistir):
    menu_id = persistir(crear_menu_del_dia())

    primero = cliente.delete(f"{PREFIJO}/{menu_id}")
    segundo = cliente.delete(f"{PREFIJO}/{menu_id}")

    assert (primero.status_code, segundo.status_code) == (204, 204)
    assert segundo.content == b""


def test_mdd_59_asignar_fecha_a_un_menu_dado_de_baja_responde_409(
    cliente, crear_menu_del_dia, persistir
):
    menu_id = persistir(crear_menu_del_dia())
    assert cliente.delete(f"{PREFIJO}/{menu_id}").status_code == 204

    respuesta = cliente.post(
        "/productos-menu", json={"menu_del_dia_id": menu_id, "fecha": "2026-07-01"}
    )

    assert respuesta.status_code == 409


def test_mdd_60_reactivar_permite_asignar_fechas_de_nuevo(cliente, crear_menu_del_dia, persistir):
    menu_id = persistir(crear_menu_del_dia())
    assert cliente.delete(f"{PREFIJO}/{menu_id}").status_code == 204

    reactivado = cliente.put(f"{PREFIJO}/{menu_id}", json=_cuerpo_put(dado_de_baja=False))
    alta = cliente.post("/productos-menu", json={"menu_del_dia_id": menu_id, "fecha": "2026-07-01"})

    assert reactivado.status_code == 200
    assert alta.status_code == 201


def test_mdd_61_reactivar_con_nombre_duplicado_responde_409_y_sigue_dado_de_baja(
    cliente, crear_menu_del_dia, persistir
):
    baja_id = persistir(crear_menu_del_dia())
    assert cliente.delete(f"{PREFIJO}/{baja_id}").status_code == 204
    persistir(crear_menu_del_dia())  # mismo nombre, activo

    respuesta = cliente.put(f"{PREFIJO}/{baja_id}", json=_cuerpo_put(dado_de_baja=False))

    assert respuesta.status_code == 409
    assert cliente.get(f"{PREFIJO}/{baja_id}").json()["dado_de_baja"] is True


def test_mdd_62_baja_de_plato_postre_y_bebida_con_fechas_futuras_es_exitosa(
    cliente, crear_menu_del_dia, crear_producto_menu, crear_plato, crear_bebida, crear_postre, persistir
):
    menu = crear_menu_del_dia()
    persistir(menu, crear_producto_menu(menu, MANANA))
    plato_id = persistir(crear_plato())
    bebida_id = persistir(crear_bebida())
    postre_id = persistir(crear_postre())

    for ruta, producto_id in (
        ("platos", plato_id),
        ("bebidas", bebida_id),
        ("postres", postre_id),
    ):
        assert cliente.delete(f"/productos/{ruta}/{producto_id}").status_code == 204
