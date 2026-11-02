from decimal import Decimal

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError

from src.productos.platos.models import Plato
from src.secciones.exceptions import (
    NombreSeccionDuplicado,
    PosicionSeccionDuplicada,
    SeccionNoEncontrada,
)
from src.secciones.models import Seccion
from src.secciones.schemas import SeccionActualizar, SeccionCrear
from src.secciones import services as servicios
from src.secciones.services import obtener_seccion


def contar_secciones(sesion) -> int:
    return sesion.scalar(select(func.count()).select_from(Seccion))


def test_posicion_crear_seccion_persiste_la_posicion_informada(sesion):
    creada = servicios.crear_seccion(
        sesion, SeccionCrear(nombre="Entradas", posicion=4)
    )

    assert sesion.get(Seccion, creada.id).posicion == 4


def test_posicion_actualizar_seccion_persiste_la_nueva_posicion(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", posicion=1))

    servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", posicion=5)
    )

    assert sesion.get(Seccion, seccion_id).posicion == 5


# --- obtener_seccion ---


def test_sec_22_obtener_seccion_existente_devuelve_la_fila(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = obtener_seccion(sesion, seccion_id)

    assert isinstance(seccion, Seccion)
    assert seccion.id == seccion_id
    assert seccion.nombre == "Entradas"
    assert seccion.subtitulo == "Para comenzar"


def test_sec_23_obtener_seccion_inexistente_lanza_no_encontrada(sesion):
    with pytest.raises(SeccionNoEncontrada):
        obtener_seccion(sesion, 999)


@pytest.mark.parametrize(
    "operacion",
    [
        lambda sesion: obtener_seccion(sesion, 999),
        lambda sesion: servicios.actualizar_seccion(
            sesion, 999, SeccionActualizar(nombre="Pastas", posicion=1)
        ),
        lambda sesion: servicios.eliminar_seccion(sesion, 999),
    ],
    ids=["obtener", "actualizar", "eliminar"],
)
def test_seccion_inexistente_no_deja_la_transaccion_abierta(sesion, operacion):
    with pytest.raises(SeccionNoEncontrada):
        operacion(sesion)
    assert not sesion.in_transaction()


def test_sec_24_listar_secciones_devuelve_todas_ordenadas_por_posicion(
    sesion, crear_seccion, persistir
):
    segunda_id = persistir(crear_seccion(nombre="Postres", posicion=2))
    primera_id = persistir(crear_seccion(nombre="Entradas", posicion=1))

    secciones = servicios.listar_secciones(sesion)

    assert [seccion.id for seccion in secciones] == [primera_id, segunda_id]


def test_sec_24_listar_secciones_sin_filas_devuelve_lista_vacia(sesion):
    assert servicios.listar_secciones(sesion) == []


# --- crear_seccion ---


def test_sec_19_crear_seccion_con_todos_los_campos_devuelve_id(sesion):
    seccion = servicios.crear_seccion(
        sesion, SeccionCrear(nombre="Entradas", subtitulo="Para comenzar", posicion=1)
    )

    assert seccion.id is not None
    assert seccion.nombre == "Entradas"
    assert seccion.subtitulo == "Para comenzar"
    assert sesion.get(Seccion, seccion.id) is seccion


def test_sec_20_crear_seccion_sin_subtitulo_queda_en_none(sesion):
    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))

    assert seccion.subtitulo is None


def test_crear_seccion_persiste_el_nombre_normalizado(sesion):
    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="  Entrádas ", posicion=1))

    assert seccion.nombre == "Entrádas"
    assert seccion.nombre_normalizado == "entrádas"


@pytest.mark.parametrize(
    "nombre",
    [
        pytest.param("Entradas", id="sec_11_exacto"),
        pytest.param("entradas", id="test_sec_12_mayusculas"),
        pytest.param("  Entradas ", id="test_sec_13_espacios"),
    ],
)
def test_sec_11_a_13_nombre_duplicado_lanza_error_sin_fila_nueva(
    sesion, crear_seccion, persistir, nombre
):
    persistir(crear_seccion(nombre="Entradas"))

    with pytest.raises(NombreSeccionDuplicado):
        servicios.crear_seccion(sesion, SeccionCrear(nombre=nombre, posicion=1))

    assert contar_secciones(sesion) == 1
    assert not sesion.new


def test_sec_14_tildes_distintas_crean_otra_seccion(sesion):
    servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))

    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entrádas", posicion=2))

    assert seccion.id is not None
    assert contar_secciones(sesion) == 2


def test_integrity_error_ajeno_a_nombre_normalizado_se_propaga(sesion, monkeypatch):
    def commit_fallido():
        raise IntegrityError("INSERT", {}, Exception("otra restricción violada"))

    monkeypatch.setattr(sesion, "commit", commit_fallido)

    with pytest.raises(IntegrityError):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))


# --- unicidad de la posición: alta ---


def test_pos_11_verificar_unicidad_con_posicion_repetida_lanza_error(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))

    with pytest.raises(PosicionSeccionDuplicada):
        servicios._verificar_unicidad(sesion, "postres", 1)

    assert not sesion.in_transaction()


def test_posicion_verificar_unicidad_con_excluir_id_ignora_la_propia_fila(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", posicion=1))

    servicios._verificar_unicidad(sesion, "entradas", 1, excluir_id=seccion_id)


def test_posicion_verificar_unicidad_con_nombre_y_posicion_libres_no_lanza(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))

    servicios._verificar_unicidad(sesion, "postres", 2)


def test_pos_11_crear_con_posicion_repetida_lanza_error_sin_fila_nueva(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))

    with pytest.raises(PosicionSeccionDuplicada):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Postres", posicion=1))

    assert not sesion.in_transaction()
    assert not sesion.new
    assert contar_secciones(sesion) == 1


def test_pos_16_una_colision_no_desplaza_a_otras_secciones(
    sesion, crear_seccion, persistir
):
    persistir(
        crear_seccion(nombre="Entradas", posicion=1),
        crear_seccion(nombre="Vecino", posicion=2),
        crear_seccion(nombre="Bebidas", posicion=3),
    )

    with pytest.raises(PosicionSeccionDuplicada):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Postres", posicion=2))

    posiciones = dict(sesion.execute(select(Seccion.nombre, Seccion.posicion)).all())
    assert posiciones == {"Entradas": 1, "Vecino": 2, "Bebidas": 3}


def test_pos_23_doble_colision_en_el_alta_lanza_el_error_de_nombre(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))

    with pytest.raises(NombreSeccionDuplicado):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))

    assert not sesion.in_transaction()
    assert contar_secciones(sesion) == 1


def test_pos_17_la_posicion_se_reutiliza_tras_el_borrado(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", posicion=1))
    servicios.eliminar_seccion(sesion, seccion_id)

    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Postres", posicion=1))

    assert seccion.posicion == 1


def test_pos_19_se_permiten_huecos_en_las_posiciones(sesion):
    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=10))

    assert seccion.posicion == 10


# --- actualizar_seccion ---


def test_sec_25_actualizar_reemplaza_nombre_y_subtitulo(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = servicios.actualizar_seccion(
        sesion,
        seccion_id,
        SeccionActualizar(nombre="Aperitivos", subtitulo="Para compartir", posicion=1),
    )

    assert seccion.nombre == "Aperitivos"
    assert seccion.nombre_normalizado == "aperitivos"
    assert seccion.subtitulo == "Para compartir"


def test_sec_26_subtitulo_omitido_queda_en_none(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", posicion=1)
    )

    assert seccion.subtitulo is None


def test_sec_27_actualizar_inexistente_lanza_no_encontrada(sesion):
    with pytest.raises(SeccionNoEncontrada):
        servicios.actualizar_seccion(sesion, 999, SeccionActualizar(nombre="Entradas", posicion=1))


def test_sec_29_no_encontrada_tiene_prioridad_sobre_duplicado(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas"))

    with pytest.raises(SeccionNoEncontrada):
        servicios.actualizar_seccion(sesion, 999, SeccionActualizar(nombre="Entradas", posicion=1))


def test_sec_15_duplicado_en_modificacion_no_cambia_la_seccion(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas"))
    postres_id = persistir(crear_seccion(nombre="Postres", subtitulo="Dulces"))

    with pytest.raises(NombreSeccionDuplicado):
        servicios.actualizar_seccion(
            sesion, postres_id, SeccionActualizar(nombre="entradas", subtitulo="Otro", posicion=1)
        )

    seccion = sesion.get(Seccion, postres_id)
    assert seccion.nombre == "Postres"
    assert seccion.nombre_normalizado == "postres"
    assert seccion.subtitulo == "Dulces"


def test_sec_16_conserva_el_propio_nombre(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", subtitulo="Nuevo", posicion=1)
    )

    assert seccion.subtitulo == "Nuevo"


def test_sec_17_cambio_solo_de_mayusculas_recalcula_el_nombre_normalizado(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="ENTRADAS", posicion=1)
    )

    assert seccion.nombre == "ENTRADAS"
    assert seccion.nombre_normalizado == "entradas"


def test_sec_44_subtitulo_de_espacios_se_persiste_como_null(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", subtitulo="   ", posicion=1)
    )

    sesion.expire_all()
    assert sesion.get(Seccion, seccion_id).subtitulo is None


def test_sec_30_actualizar_no_altera_el_seccion_id_de_los_productos(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))
    plato_id = persistir(
        Plato(
            nombre="Milanesa",
            nombre_normalizado="milanesa",
            precio=Decimal("1500.00"),
            cant_personas=2,
            seccion_id=seccion_id,
        )
    )

    servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Aperitivos", posicion=1)
    )

    sesion.expire_all()
    assert sesion.get(Plato, plato_id).seccion_id == seccion_id


# --- unicidad de la posición: modificación ---


def posiciones_por_nombre(sesion) -> dict[str, int]:
    sesion.expire_all()
    return dict(sesion.execute(select(Seccion.nombre, Seccion.posicion)).all())


def test_pos_13_posicion_repetida_en_la_modificacion_no_cambia_ninguna_seccion(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))
    postres_id = persistir(crear_seccion(nombre="Postres", posicion=2))

    with pytest.raises(PosicionSeccionDuplicada):
        servicios.actualizar_seccion(
            sesion, postres_id, SeccionActualizar(nombre="Postres", posicion=1)
        )

    assert not sesion.in_transaction()
    assert posiciones_por_nombre(sesion) == {"Entradas": 1, "Postres": 2}


def test_pos_14_la_modificacion_conserva_la_propia_posicion(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", posicion=3))

    seccion = servicios.actualizar_seccion(
        sesion,
        seccion_id,
        SeccionActualizar(nombre="Entradas", subtitulo="Nuevo", posicion=3),
    )

    assert seccion.subtitulo == "Nuevo"
    assert seccion.posicion == 3


def test_pos_15_mover_una_seccion_a_una_posicion_libre(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", posicion=1))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", posicion=5)
    )

    assert seccion.posicion == 5


def test_pos_26_doble_colision_en_la_modificacion_lanza_el_error_de_nombre(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))
    postres_id = persistir(crear_seccion(nombre="Postres", posicion=2))

    with pytest.raises(NombreSeccionDuplicado):
        servicios.actualizar_seccion(
            sesion, postres_id, SeccionActualizar(nombre="entradas", posicion=1)
        )

    assert not sesion.in_transaction()
    assert posiciones_por_nombre(sesion) == {"Entradas": 1, "Postres": 2}


def test_pos_27_no_encontrada_tiene_prioridad_sobre_posicion_duplicada(
    sesion, crear_seccion, persistir
):
    # Guarda del orden 404 -> 409: nace verde porque `obtener_seccion` ya precede al resto.
    persistir(crear_seccion(nombre="Entradas", posicion=1))

    with pytest.raises(SeccionNoEncontrada):
        servicios.actualizar_seccion(
            sesion, 999, SeccionActualizar(nombre="Postres", posicion=1)
        )

    assert not sesion.in_transaction()


def test_pos_21_el_intercambio_directo_es_rechazado(sesion, crear_seccion, persistir):
    a_id = persistir(crear_seccion(nombre="A", posicion=1))
    persistir(crear_seccion(nombre="B", posicion=2))

    with pytest.raises(PosicionSeccionDuplicada):
        servicios.actualizar_seccion(
            sesion, a_id, SeccionActualizar(nombre="A", posicion=2)
        )

    assert not sesion.in_transaction()
    assert posiciones_por_nombre(sesion) == {"A": 1, "B": 2}


def test_pos_20_intercambio_de_dos_secciones_en_tres_modificaciones(
    sesion, crear_seccion, persistir
):
    a_id = persistir(crear_seccion(nombre="A", posicion=1))
    b_id = persistir(crear_seccion(nombre="B", posicion=2))

    servicios.actualizar_seccion(sesion, a_id, SeccionActualizar(nombre="A", posicion=99))
    servicios.actualizar_seccion(sesion, b_id, SeccionActualizar(nombre="B", posicion=1))
    servicios.actualizar_seccion(sesion, a_id, SeccionActualizar(nombre="A", posicion=2))

    assert posiciones_por_nombre(sesion) == {"A": 2, "B": 1}


# --- _confirmar: traducción del IntegrityError (ruta de carrera) ---


@pytest.fixture
def sin_verificacion_previa(monkeypatch):
    """Anula `_verificar_unicidad` para que la colisión llegue al índice único."""
    monkeypatch.setattr(servicios, "_verificar_unicidad", lambda *args, **kwargs: None)


def test_pos_11_colision_solo_de_posicion_en_el_alta_se_traduce_desde_el_indice(
    sesion, crear_seccion, persistir, sin_verificacion_previa
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))

    with pytest.raises(PosicionSeccionDuplicada):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Postres", posicion=1))

    assert not sesion.in_transaction()
    assert posiciones_por_nombre(sesion) == {"Entradas": 1}


def test_pos_11_colision_solo_de_posicion_en_el_put_se_traduce_desde_el_indice(
    sesion, crear_seccion, persistir, sin_verificacion_previa
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))
    postres_id = persistir(crear_seccion(nombre="Postres", posicion=2))

    with pytest.raises(PosicionSeccionDuplicada):
        servicios.actualizar_seccion(
            sesion, postres_id, SeccionActualizar(nombre="Postres", posicion=1)
        )

    assert not sesion.in_transaction()
    assert posiciones_por_nombre(sesion) == {"Entradas": 1, "Postres": 2}


# Nota: SQLite informa una sola restricción ante una doble colisión real, por lo que la
# prioridad `nombre` → `posicion` de POS-23 y POS-26 la garantiza `_verificar_unicidad`
# (probada arriba); aquí se prueba la inspección del mensaje cuando menciona ambas.


@pytest.mark.parametrize(
    "mensaje",
    [
        "UNIQUE constraint failed: seccion.posicion, seccion.nombre_normalizado",
        "UNIQUE constraint failed: seccion.nombre_normalizado, seccion.posicion",
    ],
    ids=["posicion_primero", "nombre_primero"],
)
def test_pos_23_pos_26_nombre_normalizado_se_inspecciona_antes_que_posicion(
    sesion, monkeypatch, mensaje
):
    def commit_fallido():
        raise IntegrityError("INSERT", {}, Exception(mensaje))

    monkeypatch.setattr(sesion, "commit", commit_fallido)

    with pytest.raises(NombreSeccionDuplicado):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))

    assert not sesion.in_transaction()


def test_integrity_error_ajeno_deja_la_transaccion_cerrada_y_se_propaga(
    sesion, monkeypatch
):
    def commit_fallido():
        raise IntegrityError("INSERT", {}, Exception("otra restricción violada"))

    monkeypatch.setattr(sesion, "commit", commit_fallido)

    with pytest.raises(IntegrityError):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))

    assert not sesion.in_transaction()


# --- eliminar_seccion ---


def test_sec_31_eliminar_borra_la_fila(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))

    servicios.eliminar_seccion(sesion, seccion_id)

    assert sesion.get(Seccion, seccion_id) is None
    assert contar_secciones(sesion) == 0


def test_sec_32_eliminar_inexistente_lanza_no_encontrada(sesion):
    with pytest.raises(SeccionNoEncontrada):
        servicios.eliminar_seccion(sesion, 999)


def test_sec_33_eliminar_repetido_lanza_no_encontrada(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))
    servicios.eliminar_seccion(sesion, seccion_id)

    with pytest.raises(SeccionNoEncontrada):
        servicios.eliminar_seccion(sesion, seccion_id)


def test_sec_18_el_nombre_se_reutiliza_tras_el_borrado(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))
    servicios.eliminar_seccion(sesion, seccion_id)

    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas", posicion=1))

    assert seccion.id is not None


def test_eliminar_no_carga_los_productos_de_la_seccion(
    sesion, motor, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))
    persistir(
        Plato(
            nombre="Milanesa",
            nombre_normalizado="milanesa",
            precio=Decimal("1500.00"),
            cant_personas=2,
            seccion_id=seccion_id,
        )
    )
    sentencias = []

    def capturar(conexion, cursor, sentencia, parametros, contexto, many):
        sentencias.append(sentencia.strip().upper())

    event.listen(motor, "before_cursor_execute", capturar)
    try:
        servicios.eliminar_seccion(sesion, seccion_id)
    finally:
        event.remove(motor, "before_cursor_execute", capturar)

    borrados = [sql for sql in sentencias if sql.startswith("DELETE")]
    assert len(borrados) == 1
    assert borrados[0].startswith("DELETE FROM SECCION")
    assert not any(
        sql.startswith("SELECT") and "FROM PRODUCTO" in sql for sql in sentencias
    )


# --- liberación de posiciones tras el borrado (caracterización) ---


def test_pos_18_el_borrado_no_renumera_las_demas_secciones(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas", posicion=1))
    postres_id = persistir(crear_seccion(nombre="Postres", posicion=2))
    persistir(crear_seccion(nombre="Bebidas", posicion=3))

    servicios.eliminar_seccion(sesion, postres_id)

    assert posiciones_por_nombre(sesion) == {"Entradas": 1, "Bebidas": 3}


def test_pos_17_crear_en_la_posicion_liberada_por_el_borrado(
    sesion, crear_seccion, persistir
):
    entradas_id = persistir(crear_seccion(nombre="Entradas", posicion=1))
    servicios.eliminar_seccion(sesion, entradas_id)

    servicios.crear_seccion(sesion, SeccionCrear(nombre="Postres", posicion=1))

    assert posiciones_por_nombre(sesion) == {"Postres": 1}
