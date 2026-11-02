from src.productos import constants as constantes


def test_valores_de_tipos():
    assert constantes.TIPO_PLATO == "plato"
    assert constantes.TIPO_BEBIDA == "bebida"
    assert constantes.TIPO_POSTRE == "postre"
    assert constantes.TIPO_MENU_EJECUTIVO == "menu_ejecutivo"
    assert constantes.TIPO_COMBO_PROMOCION == "combo_promocion"


def test_valores_de_limites():
    assert constantes.NOMBRE_MAX == 100
    assert constantes.DESCRIPCION_MAX == 500
    assert constantes.PRECIO_DIGITOS == 10
    assert constantes.PRECIO_DECIMALES == 2
    assert constantes.TIPO_MAX == 30


def test_tipos_distintos_y_caben_en_tipo_max():
    tipos = [
        constantes.TIPO_PLATO,
        constantes.TIPO_BEBIDA,
        constantes.TIPO_POSTRE,
        constantes.TIPO_MENU_EJECUTIVO,
        constantes.TIPO_COMBO_PROMOCION,
    ]
    assert len(set(tipos)) == len(tipos)
    assert all(len(tipo) <= constantes.TIPO_MAX for tipo in tipos)
