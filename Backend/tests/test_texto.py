from src import texto
from src.productos import services


def test_texto_normalizar_nombre_recorta_y_casefold():
    assert texto.normalizar_nombre("  Entrádas ") == "entrádas"


def test_texto_normalizar_nombre_distingue_tildes():
    assert texto.normalizar_nombre("Entradas") != texto.normalizar_nombre("Entrádas")


def test_texto_normalizar_nombre_aplica_casefold():
    assert texto.normalizar_nombre("Straße") == "strasse"


def test_texto_productos_reexporta_el_mismo_objeto():
    assert services.normalizar_nombre is texto.normalizar_nombre
