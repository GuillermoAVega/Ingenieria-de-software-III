from datetime import date

import pytest
from sqlalchemy import select

from src.productos_menu.models import ProductoMenu

URL = "/productos-menu"
F1 = date(2026, 7, 1)
F2 = date(2026, 7, 2)
F3 = date(2026, 7, 3)


def _estado(sesion):
    """Conjunto persistido (id, producto_id, fecha); deja la transacción cerrada."""
    estado = set(
        sesion.execute(
            select(ProductoMenu.id, ProductoMenu.producto_id, ProductoMenu.fecha)
        ).all()
    )
    sesion.rollback()
    return estado


def _de_baja(producto):
    producto.dado_de_baja = True
    return producto


def test_pmd_21_mover_a_fecha_libre_responde_200_y_libera_la_anterior(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.put(f"{URL}/{menu_id}", json={"fecha": F2.isoformat()})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": menu_id, "producto_id": plato_id, "fecha": "2026-07-02"}
    assert _estado(sesion) == {(menu_id, plato_id, F2)}
    # F1 quedó libre
    assert (
        cliente.post(URL, json={"producto_id": plato_id, "fecha": F1.isoformat()}).status_code
        == 201
    )


def test_pmd_22_conservar_la_fecha_propia_responde_200(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.put(f"{URL}/{menu_id}", json={"fecha": F1.isoformat()})

    assert respuesta.status_code == 200
    assert _estado(sesion) == {(menu_id, plato_id, F1)}


def test_pmd_23_fecha_ocupada_por_otro_registro_responde_409_sin_cambios(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    plato_id, primero, segundo = persistir(
        plato, crear_producto_menu(plato, F1), crear_producto_menu(plato, F2)
    )
    antes = _estado(sesion)

    respuesta = cliente.put(f"{URL}/{primero}", json={"fecha": F2.isoformat()})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "Ya existe un menú del día en esa fecha"}
    assert antes == {(primero, plato_id, F1), (segundo, plato_id, F2)}
    assert _estado(sesion) == antes


def test_pmd_24_id_inexistente_responde_404(cliente):
    respuesta = cliente.put(f"{URL}/999", json={"fecha": F1.isoformat()})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Menú del día no encontrado"}


@pytest.mark.parametrize(
    "fecha",
    [
        pytest.param(F2, id="fecha_libre"),
        pytest.param(F1, id="misma_fecha"),
    ],
)
def test_pmd_25_producto_dado_de_baja_responde_409_sin_cambios(
    cliente, sesion, crear_plato, crear_producto_menu, persistir, fecha
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))
    plato_persistido = sesion.get(type(plato), plato_id)
    plato_persistido.dado_de_baja = True
    sesion.commit()
    sesion.close()

    respuesta = cliente.put(f"{URL}/{menu_id}", json={"fecha": fecha.isoformat()})

    assert respuesta.status_code == 409
    assert _estado(sesion) == {(menu_id, plato_id, F1)}


def test_pmd_26_producto_id_del_cuerpo_se_ignora(
    cliente, sesion, crear_plato, crear_postre, crear_producto_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    plato_id, postre_id, menu_id = persistir(plato, postre, crear_producto_menu(plato, F1))

    respuesta = cliente.put(
        f"{URL}/{menu_id}", json={"fecha": F2.isoformat(), "producto_id": postre_id}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["producto_id"] == plato_id
    assert _estado(sesion) == {(menu_id, plato_id, F2)}


@pytest.mark.parametrize(
    "cuerpo",
    [
        pytest.param({}, id="fecha_ausente"),
        pytest.param({"fecha": "no-es-una-fecha"}, id="fecha_invalida"),
        pytest.param({"fecha": "2026-02-30"}, id="fecha_inexistente"),
    ],
)
def test_pmd_27_fecha_ausente_o_invalida_responde_422_sin_cambios(
    cliente, sesion, crear_plato, crear_producto_menu, persistir, cuerpo
):
    plato = crear_plato()
    plato_id, menu_id = persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.put(f"{URL}/{menu_id}", json=cuerpo)

    assert respuesta.status_code == 422
    assert _estado(sesion) == {(menu_id, plato_id, F1)}


def test_pmd_28_esquema_invalido_prevalece_sobre_id_inexistente(cliente):
    respuesta = cliente.put(f"{URL}/999", json={"fecha": "no-es-una-fecha"})

    assert respuesta.status_code == 422


def test_pmd_29_id_inexistente_prevalece_sobre_fecha_ocupada(
    cliente, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    persistir(plato, crear_producto_menu(plato, F1))

    respuesta = cliente.put(f"{URL}/999", json={"fecha": F1.isoformat()})

    assert respuesta.status_code == 404


def test_pmd_30_baja_prevalece_sobre_fecha_ocupada_con_mensaje_distinto(
    cliente, sesion, crear_plato, crear_postre, crear_producto_menu, persistir
):
    plato, postre = crear_plato(), crear_postre()
    _, postre_id, menu_baja, _ = persistir(
        plato,
        postre,
        crear_producto_menu(postre, F1),
        crear_producto_menu(plato, F2),
    )
    sesion.get(type(postre), postre_id).dado_de_baja = True
    sesion.commit()
    sesion.close()

    respuesta = cliente.put(f"{URL}/{menu_baja}", json={"fecha": F2.isoformat()})

    assert respuesta.status_code == 409
    assert respuesta.json() == {"detail": "El producto está dado de baja"}


def test_pmd_31_los_rechazos_422_404_y_409_no_cambian_lo_persistido(
    cliente, sesion, crear_plato, crear_producto_menu, persistir
):
    plato = crear_plato()
    _, primero, _ = persistir(
        plato, crear_producto_menu(plato, F1), crear_producto_menu(plato, F2)
    )
    antes = _estado(sesion)

    rechazos = [
        (f"{URL}/{primero}", {"fecha": "no-es-una-fecha"}, 422),
        (f"{URL}/999", {"fecha": F3.isoformat()}, 404),
        (f"{URL}/{primero}", {"fecha": F2.isoformat()}, 409),
    ]
    for url, cuerpo, codigo in rechazos:
        assert cliente.put(url, json=cuerpo).status_code == codigo
        assert _estado(sesion) == antes
