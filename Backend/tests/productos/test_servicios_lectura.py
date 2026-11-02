import ast
from datetime import date
from pathlib import Path

import pytest

from src.productos import services
from src.productos.exceptions import NombreDuplicado, ProductoNoEncontrado
from src.productos.platos.models import Plato


def test_obtener_hoy_devuelve_la_fecha_actual():
    assert services.obtener_hoy() == date.today()


def test_normalizar_nombre_recorta_y_pasa_a_minusculas():
    assert services.normalizar_nombre("  Milanesa ") == "milanesa"


def test_normalizar_nombre_distingue_tildes():
    assert services.normalizar_nombre("Milanesa") != services.normalizar_nombre("Milanésa")


def test_normalizar_nombre_aplica_casefold():
    assert services.normalizar_nombre("Straße") == "strasse"


def test_cat_10_obtener_devuelve_un_producto_dado_de_baja(sesion, crear_plato):
    plato = crear_plato(dado_de_baja=True)
    sesion.add(plato)
    sesion.commit()

    obtenido = services.obtener(sesion, Plato, plato.id)

    assert obtenido.id == plato.id
    assert obtenido.dado_de_baja is True


def test_cat_08_obtener_con_id_inexistente_lanza_producto_no_encontrado(sesion):
    with pytest.raises(ProductoNoEncontrado):
        services.obtener(sesion, Plato, 999)


def test_cat_08_obtener_con_id_de_otro_subtipo_lanza_producto_no_encontrado(
    sesion, crear_bebida
):
    bebida = crear_bebida()
    sesion.add(bebida)
    sesion.commit()

    with pytest.raises(ProductoNoEncontrado):
        services.obtener(sesion, Plato, bebida.id)


def test_cat_21_verificar_nombre_unico_rechaza_un_nombre_activo(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        services.verificar_nombre_unico(sesion, "Milanesa")


def test_cat_21_verificar_nombre_unico_es_global_entre_subtipos(sesion, crear_bebida):
    sesion.add(crear_bebida(nombre="Milanesa"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        services.verificar_nombre_unico(sesion, "Milanesa")


def test_cat_22_verificar_nombre_unico_ignora_mayusculas(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        services.verificar_nombre_unico(sesion, "MILANESA")


def test_cat_23_verificar_nombre_unico_ignora_espacios_sobrantes(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        services.verificar_nombre_unico(sesion, "  Milanesa ")


def test_cat_24_verificar_nombre_unico_distingue_tildes(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa"))
    sesion.commit()

    services.verificar_nombre_unico(sesion, "Milanésa")


def test_cat_25_verificar_nombre_unico_ignora_los_dados_de_baja(sesion, crear_plato):
    sesion.add(crear_plato(nombre="Milanesa", dado_de_baja=True))
    sesion.commit()

    services.verificar_nombre_unico(sesion, "Milanesa")


def test_cat_26_verificar_nombre_unico_excluye_el_propio_id(sesion, crear_plato):
    plato = crear_plato(nombre="Milanesa")
    sesion.add(plato)
    sesion.commit()

    services.verificar_nombre_unico(sesion, "Milanesa", excluir_id=plato.id)


def test_cat_26_excluir_un_id_no_oculta_a_otro_producto_activo(
    sesion, crear_plato, crear_postre
):
    postre = crear_postre(nombre="Flan")
    sesion.add_all([crear_plato(nombre="Milanesa"), postre])
    sesion.commit()

    with pytest.raises(NombreDuplicado):
        services.verificar_nombre_unico(sesion, "Milanesa", excluir_id=postre.id)


def test_el_modulo_de_servicios_compartidos_no_importa_subpaquetes_ni_fastapi():
    fuente = Path(services.__file__).read_text(encoding="utf-8")
    importados = []
    for nodo in ast.walk(ast.parse(fuente)):
        if isinstance(nodo, ast.Import):
            importados += [alias.name for alias in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            importados.append(nodo.module or "")

    assert not [m for m in importados if m.startswith("fastapi")]
    for sub in ("platos", "bebidas", "postres", "menus_ejecutivos", "combos"):
        assert not [m for m in importados if m.startswith(f"src.productos.{sub}")]
