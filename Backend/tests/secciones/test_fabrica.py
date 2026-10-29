from sqlalchemy import select

from src.productos.registro import Seccion


def test_fabrica_crear_seccion_persiste_y_calcula_nombre_normalizado(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="  Entrádas "))

    seccion = sesion.scalars(select(Seccion).where(Seccion.id == seccion_id)).one()
    assert seccion.nombre == "  Entrádas "
    assert seccion.nombre_normalizado == "entrádas"
    assert seccion.subtitulo is None


def test_fabrica_crear_seccion_acepta_subtitulo(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    assert sesion.get(Seccion, seccion_id).subtitulo == "Para comenzar"


def test_fabrica_crear_seccion_autoasigna_posiciones_unicas_desde_1001(crear_seccion):
    assert crear_seccion(nombre="Entradas").posicion == 1001
    assert crear_seccion(nombre="Postres").posicion == 1002


def test_fabrica_crear_seccion_reinicia_el_contador_en_cada_prueba(crear_seccion):
    assert crear_seccion(nombre="Entradas").posicion == 1001


def test_fabrica_crear_seccion_respeta_posicion_explicita(crear_seccion):
    assert crear_seccion(nombre="Entradas", posicion=7).posicion == 7
    assert crear_seccion(nombre="Postres").posicion == 1001
