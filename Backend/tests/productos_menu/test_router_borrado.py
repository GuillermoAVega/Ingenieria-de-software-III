from datetime import date

from sqlalchemy import select

from src.productos.menus_del_dia.models import MenuDelDia
from src.productos_menu.models import ProductoMenu

URL = "/productos-menu"
F1 = date(2026, 7, 1)


def _estado(sesion):
    """Conjunto persistido (id, menu_del_dia_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.menu_del_dia_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


def test_pmd_32_borrado_exitoso_responde_204_sin_cuerpo_y_elimina_el_registro(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.delete(f"{URL}/{menu_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert _estado(sesion) == set()
    # El producto sigue existiendo
    assert sesion.get(MenuDelDia, menu_del_dia_id) is not None


def test_pmd_33_id_inexistente_responde_404(cliente):
    respuesta = cliente.delete(f"{URL}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Menú del día no encontrado"}


def test_pmd_34_delete_repetido_responde_404(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    _, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))

    assert cliente.delete(f"{URL}/{menu_id}").status_code == 204
    assert cliente.delete(f"{URL}/{menu_id}").status_code == 404


def test_pmd_35_el_estado_del_producto_no_se_verifica_al_borrar(
    cliente, sesion, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia(dado_de_baja=True)
    _, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))

    respuesta = cliente.delete(f"{URL}/{menu_id}")

    assert respuesta.status_code == 204
    assert _estado(sesion) == set()


def test_pmd_36_la_fecha_liberada_puede_reutilizarse(
    cliente, crear_menu_del_dia, crear_producto_menu, persistir
):
    mdd = crear_menu_del_dia()
    menu_del_dia_id, menu_id = persistir(mdd, crear_producto_menu(mdd, F1))
    assert cliente.delete(f"{URL}/{menu_id}").status_code == 204

    respuesta = cliente.post(URL, json={"menu_del_dia_id": menu_del_dia_id, "fecha": F1.isoformat()})

    assert respuesta.status_code == 201
