from src.secciones import constants


def test_constantes_valores():
    assert constants.NOMBRE_MAX == 100
    assert constants.SUBTITULO_MAX == 200
    assert constants.PREFIJO == "/secciones"
