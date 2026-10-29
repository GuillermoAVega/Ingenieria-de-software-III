"""Integración de `seccion_id` en los servicios compartidos de productos (nivel servicio)."""
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import event, select, text

from src.productos import services
from src.productos.bebidas import services as servicios_bebidas
from src.productos.bebidas.schemas import BebidaActualizar, BebidaCrear
from src.productos.exceptions import NombreDuplicado, ProductoNoEncontrado, SeccionInexistente
from src.productos.combos.models import ComboPromocion
from src.productos.models import Producto
from src.productos.platos import services as servicios_platos
from src.productos.platos.models import Plato
from src.productos.platos.schemas import PlatoActualizar, PlatoCrear
from src.productos.postres import services as servicios_postres
from src.productos.postres.models import Postre
from src.productos.postres.schemas import PostreActualizar, PostreCrear


def _plato(cls=PlatoCrear, **cambios):
    datos = {"nombre": "Milanesa", "precio": Decimal("1500.00"), "cant_personas": 2}
    datos.update(cambios)
    return cls(**datos)


def _bebida(cls=BebidaCrear, **cambios):
    datos = {"nombre": "Cerveza", "precio": Decimal("800.00"), "es_alcoholica": True}
    datos.update(cambios)
    return cls(**datos)


def _postre(cls=PostreCrear, **cambios):
    datos = {"nombre": "Flan", "precio": Decimal("600.00")}
    datos.update(cambios)
    return cls(**datos)


def _seccion(sesion, crear_seccion, nombre="Entradas"):
    seccion = crear_seccion(nombre=nombre)
    sesion.add(seccion)
    sesion.commit()
    return seccion


def test_cat_s_01_crear_plato_con_seccion_existente_guarda_seccion_id(sesion, crear_seccion):
    seccion = _seccion(sesion, crear_seccion)

    plato = servicios_platos.crear_plato(sesion, _plato(seccion_id=seccion.id))

    assert sesion.get(Plato, plato.id).seccion_id == seccion.id


def test_cat_s_03_crear_plato_con_seccion_inexistente_no_persiste(sesion):
    with pytest.raises(SeccionInexistente) as error:
        servicios_platos.crear_plato(sesion, _plato(seccion_id=999))

    assert error.value.seccion_id == 999
    assert sesion.scalars(select(Producto)).all() == []


def test_cat_s_04_bebida_y_postre_aceptan_seccion_id_en_el_alta(sesion, crear_seccion):
    seccion = _seccion(sesion, crear_seccion)

    bebida = servicios_bebidas.crear_bebida(sesion, _bebida(seccion_id=seccion.id))
    postre = servicios_postres.crear_postre(sesion, _postre(seccion_id=seccion.id))

    assert bebida.seccion_id == seccion.id
    assert postre.seccion_id == seccion.id


def test_cat_s_05_bebida_y_postre_rechazan_seccion_inexistente_en_el_alta(sesion):
    with pytest.raises(SeccionInexistente):
        servicios_bebidas.crear_bebida(sesion, _bebida(seccion_id=999))
    with pytest.raises(SeccionInexistente):
        servicios_postres.crear_postre(sesion, _postre(seccion_id=999))

    assert sesion.scalars(select(Producto)).all() == []


def test_cat_s_02_seccion_id_none_no_consulta_secciones(sesion):
    sentencias = []
    event.listen(
        sesion.get_bind(), "before_cursor_execute",
        lambda conn, cur, sql, *resto: sentencias.append(sql),
    )

    servicios_platos.crear_plato(sesion, _plato())

    assert not any("FROM seccion" in sql for sql in sentencias)


def test_cat_s_06_actualizar_plato_cambia_la_seccion(sesion, crear_seccion, crear_plato, HOY):
    s1 = _seccion(sesion, crear_seccion, "Entradas")
    s2 = _seccion(sesion, crear_seccion, "Principales")
    plato = crear_plato(seccion_id=s1.id)
    sesion.add(plato)
    sesion.commit()

    servicios_platos.actualizar_plato(
        sesion, plato.id, _plato(PlatoActualizar, seccion_id=s2.id), hoy=HOY
    )

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).seccion_id == s2.id


def test_cat_s_07_put_sin_seccion_id_desasigna_la_seccion(
    sesion, crear_seccion, crear_plato, HOY
):
    seccion = _seccion(sesion, crear_seccion)
    plato = crear_plato(seccion_id=seccion.id)
    sesion.add(plato)
    sesion.commit()

    servicios_platos.actualizar_plato(sesion, plato.id, _plato(PlatoActualizar), hoy=HOY)

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).seccion_id is None


def test_cat_s_08_put_con_seccion_inexistente_conserva_la_seccion(
    sesion, crear_seccion, crear_plato, HOY
):
    seccion = _seccion(sesion, crear_seccion)
    plato = crear_plato(seccion_id=seccion.id)
    sesion.add(plato)
    sesion.commit()

    with pytest.raises(SeccionInexistente):
        servicios_platos.actualizar_plato(
            sesion, plato.id, _plato(PlatoActualizar, seccion_id=999), hoy=HOY
        )

    sesion.expire_all()
    assert sesion.get(Plato, plato.id).seccion_id == seccion.id


def test_cat_s_09_bebida_y_postre_aceptan_y_rechazan_seccion_id_en_el_put(
    sesion, crear_seccion, crear_bebida, crear_postre, HOY
):
    seccion = _seccion(sesion, crear_seccion)
    bebida, postre = crear_bebida(), crear_postre()
    sesion.add_all([bebida, postre])
    sesion.commit()

    servicios_bebidas.actualizar_bebida(
        sesion, bebida.id, _bebida(BebidaActualizar, seccion_id=seccion.id), hoy=HOY
    )
    servicios_postres.actualizar_postre(
        sesion, postre.id, _postre(PostreActualizar, seccion_id=seccion.id), hoy=HOY
    )
    assert bebida.seccion_id == seccion.id
    assert postre.seccion_id == seccion.id

    with pytest.raises(SeccionInexistente):
        servicios_bebidas.actualizar_bebida(
            sesion, bebida.id, _bebida(BebidaActualizar, seccion_id=999), hoy=HOY
        )
    with pytest.raises(SeccionInexistente):
        servicios_postres.actualizar_postre(
            sesion, postre.id, _postre(PostreActualizar, seccion_id=999), hoy=HOY
        )


def test_cat_s_11_asignar_seccion_a_un_producto_dado_de_baja(
    sesion, crear_seccion, crear_plato, HOY
):
    seccion = _seccion(sesion, crear_seccion)
    plato = crear_plato()
    plato.dado_de_baja = True
    sesion.add(plato)
    sesion.commit()

    servicios_platos.actualizar_plato(
        sesion, plato.id, _plato(PlatoActualizar, seccion_id=seccion.id), hoy=HOY
    )

    sesion.expire_all()
    guardado = sesion.get(Plato, plato.id)
    assert guardado.seccion_id == seccion.id
    assert guardado.dado_de_baja is True


def test_cat_s_12_el_mismo_nombre_en_otra_seccion_es_duplicado(
    sesion, crear_seccion, crear_plato
):
    s1 = _seccion(sesion, crear_seccion, "Entradas")
    s2 = _seccion(sesion, crear_seccion, "Principales")
    sesion.add(crear_plato(nombre="Milanesa", seccion_id=s1.id))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        servicios_platos.crear_plato(sesion, _plato(nombre="Milanesa", seccion_id=s2.id))


def test_cat_s_14_id_inexistente_con_seccion_inexistente_es_producto_no_encontrado(
    sesion, HOY
):
    with pytest.raises(ProductoNoEncontrado):
        servicios_platos.actualizar_plato(
            sesion, 999, _plato(PlatoActualizar, seccion_id=999), hoy=HOY
        )


def test_cat_s_18_seccion_inexistente_tiene_prioridad_sobre_nombre_duplicado(
    sesion, crear_plato, HOY
):
    sesion.add(crear_plato(nombre="Milanesa"))
    otro = crear_plato(nombre="Pizza")
    sesion.add(otro)
    sesion.commit()

    with pytest.raises(SeccionInexistente):
        servicios_platos.crear_plato(sesion, _plato(nombre="Milanesa", seccion_id=999))
    with pytest.raises(SeccionInexistente):
        servicios_platos.actualizar_plato(
            sesion, otro.id, _plato(PlatoActualizar, nombre="Milanesa", seccion_id=999), hoy=HOY
        )


def test_crear_producto_hace_rollback_ante_cualquier_error_de_dominio(sesion):
    sesion.add(Plato(nombre="Pendiente", nombre_normalizado="pendiente",
                     precio=Decimal("1.00"), cant_personas=1))
    assert sesion.new

    with pytest.raises(SeccionInexistente):
        services.crear_producto(
            sesion, Plato, _plato(seccion_id=999), cant_personas=2
        )

    assert not sesion.new


# --- Desvinculación a nivel de base de datos (ON DELETE SET NULL) ---


def _crear_cinco_subtipos(
    sesion, seccion_id, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo,
    sufijo="", vencido=False,
):
    """Persiste un producto de cada subtipo en la sección; devuelve {tipo: id}."""
    plato = crear_plato(nombre=f"Plato{sufijo}")
    bebida = crear_bebida(nombre=f"Bebida{sufijo}")
    postre = crear_postre(nombre=f"Postre{sufijo}")
    menu = crear_menu(plato, postre, nombre=f"Menu{sufijo}")
    hasta = date(2026, 6, 10) if vencido else date(2026, 6, 30)
    combo = crear_combo(nombre=f"Combo{sufijo}", hasta=hasta, platos=[plato])
    productos = {
        "plato": plato, "bebida": bebida, "postre": postre, "menu": menu, "combo": combo,
    }
    for producto in productos.values():
        producto.seccion_id = seccion_id
    sesion.add_all(productos.values())
    sesion.commit()
    return {tipo: producto.id for tipo, producto in productos.items()}


def _secciones_de_productos(sesion):
    sesion.expire_all()
    filas = sesion.execute(text("SELECT id, seccion_id FROM producto")).all()
    return dict(filas)


def test_sec_34_pragma_foreign_keys_esta_activo(sesion):
    assert sesion.execute(text("PRAGMA foreign_keys")).scalar() == 1


def test_sec_34_delete_crudo_conserva_plato_y_bebida_con_seccion_nula(
    sesion, crear_seccion, crear_plato, crear_bebida
):
    seccion = _seccion(sesion, crear_seccion)
    plato = crear_plato()
    bebida = crear_bebida()
    plato.seccion_id = bebida.seccion_id = seccion.id
    sesion.add_all([plato, bebida])
    sesion.commit()
    ids = [plato.id, bebida.id]

    sesion.execute(text("DELETE FROM seccion WHERE id = :id"), {"id": seccion.id})
    sesion.commit()

    assert sesion.execute(text("SELECT COUNT(*) FROM seccion")).scalar() == 0
    assert _secciones_de_productos(sesion) == {ids[0]: None, ids[1]: None}


def test_sec_35_delete_crudo_solo_desvincula_los_productos_de_la_seccion_borrada(
    sesion, crear_seccion, crear_plato
):
    borrada = _seccion(sesion, crear_seccion, nombre="Entradas")
    conservada = _seccion(sesion, crear_seccion, nombre="Postres")
    del_borrada = crear_plato(nombre="Milanesa")
    de_la_otra = crear_plato(nombre="Pizza")
    sin_seccion = crear_plato(nombre="Tarta")
    del_borrada.seccion_id = borrada.id
    de_la_otra.seccion_id = conservada.id
    sesion.add_all([del_borrada, de_la_otra, sin_seccion])
    sesion.commit()
    ids = (del_borrada.id, de_la_otra.id, sin_seccion.id)
    conservada_id = conservada.id

    sesion.execute(text("DELETE FROM seccion WHERE id = :id"), {"id": borrada.id})
    sesion.commit()

    assert _secciones_de_productos(sesion) == {
        ids[0]: None, ids[1]: conservada_id, ids[2]: None,
    }


def test_sec_36_delete_crudo_desvincula_los_cinco_subtipos(
    sesion, crear_seccion, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo
):
    seccion = _seccion(sesion, crear_seccion)
    ids = _crear_cinco_subtipos(
        sesion, seccion.id, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo
    )

    sesion.execute(text("DELETE FROM seccion WHERE id = :id"), {"id": seccion.id})
    sesion.commit()

    assert _secciones_de_productos(sesion) == {id_: None for id_ in ids.values()}
    assert sesion.execute(text("SELECT COUNT(*) FROM combo_promocion")).scalar() == 1
    assert sesion.execute(text("SELECT COUNT(*) FROM menu_ejecutivo")).scalar() == 1


def test_sec_37_delete_crudo_desvincula_un_combo_vencido_sin_otros_cambios(
    sesion, crear_seccion, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo
):
    seccion = _seccion(sesion, crear_seccion)
    ids = _crear_cinco_subtipos(
        sesion, seccion.id, crear_plato, crear_bebida, crear_postre, crear_menu, crear_combo,
        vencido=True,
    )

    sesion.execute(text("DELETE FROM seccion WHERE id = :id"), {"id": seccion.id})
    sesion.commit()

    combo = sesion.get(ComboPromocion, ids["combo"])
    assert combo is not None
    assert combo.seccion_id is None
    assert combo.fecha_hasta == date(2026, 6, 10)
    assert combo.dado_de_baja is False


def test_sec_38_delete_crudo_desvincula_un_postre_dado_de_baja(
    sesion, crear_seccion, crear_postre
):
    seccion = _seccion(sesion, crear_seccion)
    postre = crear_postre()
    postre.dado_de_baja = True
    postre.seccion_id = seccion.id
    sesion.add(postre)
    sesion.commit()
    postre_id = postre.id

    sesion.execute(text("DELETE FROM seccion WHERE id = :id"), {"id": seccion.id})
    sesion.commit()

    sesion.expire_all()
    conservado = sesion.get(Postre, postre_id)
    assert conservado is not None
    assert conservado.seccion_id is None
    assert conservado.dado_de_baja is True
