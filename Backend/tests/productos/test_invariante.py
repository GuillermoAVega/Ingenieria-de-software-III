"""Invariante global: un compuesto activo nunca referencia componentes inactivos (LD-23)."""

import random
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.productos.combos.models import ComboPromocion
from src.productos.menus_ejecutivos.models import MenuEjecutivo

HOY = date(2026, 6, 15)  # coincide con el HOY fijo del fixture `cliente`
SEMILLAS = [1, 2, 3, 7, 11, 42, 99, 2026]
PASOS = 80

CUERPOS_SIMPLES = {
    "platos": {"nombre": "Plato", "precio": "1500.00", "cant_personas": 2},
    "bebidas": {"nombre": "Bebida", "precio": "800.00", "es_alcoholica": False},
    "postres": {"nombre": "Postre", "precio": "600.00"},
}


def _verificar_invariante(sesion):
    """Lee el estado real de la BD y falla si algún compuesto vigente tiene componentes inactivos."""
    sesion.rollback()
    sesion.expire_all()
    for menu in sesion.scalars(select(MenuEjecutivo)):
        if not menu.dado_de_baja:
            assert not menu.plato.dado_de_baja, f"menú activo {menu.id} con plato inactivo"
            assert not menu.postre.dado_de_baja, f"menú activo {menu.id} con postre inactivo"
    for combo in sesion.scalars(select(ComboPromocion)):
        if not combo.dado_de_baja and combo.fecha_hasta >= HOY:
            componentes = [*combo.platos, *combo.bebidas, *combo.postres]
            assert all(
                not componente.dado_de_baja for componente in componentes
            ), f"combo vigente {combo.id} con componentes inactivos"
    sesion.rollback()


def _alta_componente(cliente, tipo, numero):
    cuerpo = {**CUERPOS_SIMPLES[tipo], "nombre": f"{tipo}-{numero}"}
    respuesta = cliente.post(f"/productos/{tipo}", json=cuerpo)
    assert respuesta.status_code == 201
    return respuesta.json()["id"], cuerpo


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_ld_23_invariante_se_mantiene_en_secuencias_mixtas_de_operaciones(
    cliente, sesion, crear_plato, persistir, semilla
):
    azar = random.Random(semilla)

    # Combo vencido pero activo: no bloquea bajas y puede quedar con componentes inactivos
    plato_vencido = crear_plato(nombre="Plato vencido")
    persistir(
        plato_vencido,
        _combo_vencido(plato_vencido),
    )

    componentes = {"platos": [], "bebidas": [], "postres": []}
    for tipo, cantidad in (("platos", 3), ("bebidas", 2), ("postres", 3)):
        for numero in range(cantidad):
            componentes[tipo].append(_alta_componente(cliente, tipo, numero))
    menus, combos = [], []

    def elegir(tipo):
        return azar.choice(componentes[tipo])

    def elegir_ids(tipo, maximo):
        cantidad = azar.randint(0, maximo)
        return list({azar.choice(componentes[tipo])[0] for _ in range(cantidad)})

    def baja_componente():
        tipo = azar.choice(list(componentes))
        return cliente.delete(f"/productos/{tipo}/{elegir(tipo)[0]}")

    def baja_componente_por_put():
        tipo = azar.choice(list(componentes))
        id_, cuerpo = elegir(tipo)
        return cliente.put(f"/productos/{tipo}/{id_}", json={**cuerpo, "dado_de_baja": True})

    def reactivar_componente():
        tipo = azar.choice(list(componentes))
        id_, cuerpo = elegir(tipo)
        return cliente.put(f"/productos/{tipo}/{id_}", json={**cuerpo, "dado_de_baja": False})

    def editar_componente():
        tipo = azar.choice(list(componentes))
        id_, cuerpo = elegir(tipo)
        return cliente.put(f"/productos/{tipo}/{id_}", json={**cuerpo, "precio": "999.00"})

    def cuerpo_menu(numero_nombre, **extra):
        return {
            "nombre": f"menu-{numero_nombre}",
            "precio": "2000.00",
            "plato_id": elegir("platos")[0],
            "postre_id": elegir("postres")[0],
            **extra,
        }

    def alta_menu():
        cuerpo = cuerpo_menu(azar.randint(0, 4))
        respuesta = cliente.post("/productos/menus-ejecutivos", json=cuerpo)
        if respuesta.status_code == 201:
            menus.append(respuesta.json()["id"])
        return respuesta

    def editar_menu():
        if not menus:
            return alta_menu()
        cuerpo = cuerpo_menu(azar.randint(0, 4))
        return cliente.put(
            f"/productos/menus-ejecutivos/{azar.choice(menus)}",
            json={**cuerpo, **azar.choice([{}, {"dado_de_baja": False}, {"dado_de_baja": True}])},
        )

    def baja_menu():
        if not menus:
            return alta_menu()
        return cliente.delete(f"/productos/menus-ejecutivos/{azar.choice(menus)}")

    def cuerpo_combo(**extra):
        return {
            "nombre": f"combo-{azar.randint(0, 4)}",
            "precio": "3000.00",
            "fecha_desde": "2026-06-01",
            "fecha_hasta": azar.choice(["2026-06-15", "2026-06-30", "2026-12-31"]),
            "platos_ids": elegir_ids("platos", 2),
            "bebidas_ids": elegir_ids("bebidas", 2),
            "postres_ids": elegir_ids("postres", 2),
            **extra,
        }

    def alta_combo():
        respuesta = cliente.post("/productos/combos", json=cuerpo_combo())
        if respuesta.status_code == 201:
            combos.append(respuesta.json()["id"])
        return respuesta

    def editar_combo():
        if not combos:
            return alta_combo()
        extra = azar.choice([{}, {"dado_de_baja": False}, {"dado_de_baja": True}])
        return cliente.put(f"/productos/combos/{azar.choice(combos)}", json=cuerpo_combo(**extra))

    def baja_combo():
        if not combos:
            return alta_combo()
        return cliente.delete(f"/productos/combos/{azar.choice(combos)}")

    operaciones = [
        baja_componente,
        baja_componente_por_put,
        reactivar_componente,
        editar_componente,
        alta_menu,
        editar_menu,
        baja_menu,
        alta_combo,
        editar_combo,
        baja_combo,
    ]

    for _ in range(PASOS):
        respuesta = azar.choice(operaciones)()
        assert respuesta.status_code < 500, respuesta.text
        _verificar_invariante(sesion)


def _combo_vencido(plato):
    return ComboPromocion(
        nombre="Combo vencido",
        nombre_normalizado="combo vencido",
        precio=Decimal("3000.00"),
        fecha_desde=date(2026, 5, 1),
        fecha_hasta=date(2026, 6, 14),
        platos=[plato],
    )


def test_ld_23_la_baja_bloqueada_no_rompe_el_invariante_y_la_baja_permitida_tampoco(
    cliente, sesion
):
    plato_id, _ = _alta_componente(cliente, "platos", 0)
    postre_id, _ = _alta_componente(cliente, "postres", 0)
    menu = cliente.post(
        "/productos/menus-ejecutivos",
        json={"nombre": "Menú", "precio": "2000.00", "plato_id": plato_id, "postre_id": postre_id},
    ).json()

    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 409
    _verificar_invariante(sesion)

    assert cliente.delete(f"/productos/menus-ejecutivos/{menu['id']}").status_code == 204
    assert cliente.delete(f"/productos/platos/{plato_id}").status_code == 204
    _verificar_invariante(sesion)

    # Reactivar el menú con el plato inactivo se rechaza y el estado sigue siendo consistente
    respuesta = cliente.put(
        f"/productos/menus-ejecutivos/{menu['id']}",
        json={
            "nombre": "Menú",
            "precio": "2000.00",
            "plato_id": plato_id,
            "postre_id": postre_id,
            "dado_de_baja": False,
        },
    )
    assert respuesta.status_code == 409
    _verificar_invariante(sesion)
