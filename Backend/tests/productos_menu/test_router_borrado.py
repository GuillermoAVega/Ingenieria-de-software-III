from datetime import date

from sqlalchemy import select

from src.productos.platos.models import Plato
from src.productos_menu.models import ProductoMenu

URL = "/productos-menu"
F1 = date(2026, 7, 1)


def _estado(sesion):
    """Conjunto persistido (id, producto_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.producto_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


def test_pmd_32_borrado_exitoso_responde_204_sin_cuerpo_y_elimina_el_registro(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.delete(f"{URL}/{menu_id}")

    assert respuesta.status_code == 204
    assert respuesta.content == b""
    assert _estado(sesion) == set()
    # El producto sigue existiendo
    assert sesion.get(Plato, plato_id) is not None


def test_pmd_33_id_inexistente_responde_404(cliente):
    respuesta = cliente.delete(f"{URL}/999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Menú del día no encontrado"}


def test_pmd_34_delete_repetido_responde_404(
    cliente, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    _, menu_id = persistir(plato, crear_producto_menu(plato, F1))

    assert cliente.delete(f"{URL}/{menu_id}").status_code == 204
    assert cliente.delete(f"{URL}/{menu_id}").status_code == 404


def test_pmd_35_el_estado_del_producto_no_se_verifica_al_borrar(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato(dado_de_baja=True)
    _, menu_id = persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.delete(f"{URL}/{menu_id}")

    assert respuesta.status_code == 204
    assert _estado(sesion) == set()


def test_pmd_36_la_fecha_liberada_puede_reutilizarse(
    cliente, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))
    assert cliente.delete(f"{URL}/{menu_id}").status_code == 204

    respuesta = cliente.post(URL, json={"producto_id": plato_id, "fecha": F1.isoformat()})

    assert respuesta.status_code == 201
