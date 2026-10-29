from decimal import Decimal

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError

from src.productos.platos.models import Plato
from src.secciones.exceptions import NombreSeccionDuplicado, SeccionNoEncontrada
from src.secciones.models import Seccion
from src.secciones.schemas import SeccionActualizar, SeccionCrear
from src.secciones import services as servicios
from src.secciones.services import obtener_seccion


def contar_secciones(sesion) -> int:
    return sesion.scalar(select(func.count()).select_from(Seccion))


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
            sesion, 999, SeccionActualizar(nombre="Pastas")
        ),
        lambda sesion: servicios.eliminar_seccion(sesion, 999),
    ],
    ids=["obtener", "actualizar", "eliminar"],
)
def test_seccion_inexistente_no_deja_la_transaccion_abierta(sesion, operacion):
    with pytest.raises(SeccionNoEncontrada):
        operacion(sesion)
    assert not sesion.in_transaction()


# --- crear_seccion ---


def test_sec_19_crear_seccion_con_todos_los_campos_devuelve_id(sesion):
    seccion = servicios.crear_seccion(
        sesion, SeccionCrear(nombre="Entradas", subtitulo="Para comenzar")
    )

    assert seccion.id is not None
    assert seccion.nombre == "Entradas"
    assert seccion.subtitulo == "Para comenzar"
    assert sesion.get(Seccion, seccion.id) is seccion


def test_sec_20_crear_seccion_sin_subtitulo_queda_en_none(sesion):
    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas"))

    assert seccion.subtitulo is None


def test_crear_seccion_persiste_el_nombre_normalizado(sesion):
    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="  Entrádas "))

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
        servicios.crear_seccion(sesion, SeccionCrear(nombre=nombre))

    assert contar_secciones(sesion) == 1
    assert not sesion.new


def test_sec_14_tildes_distintas_crean_otra_seccion(sesion):
    servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas"))

    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entrádas"))

    assert seccion.id is not None
    assert contar_secciones(sesion) == 2


def test_integrity_error_ajeno_a_nombre_normalizado_se_propaga(sesion, monkeypatch):
    def commit_fallido():
        raise IntegrityError("INSERT", {}, Exception("otra restricción violada"))

    monkeypatch.setattr(sesion, "commit", commit_fallido)

    with pytest.raises(IntegrityError):
        servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas"))


# --- actualizar_seccion ---


def test_sec_25_actualizar_reemplaza_nombre_y_subtitulo(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Aperitivos", subtitulo="Para compartir")
    )

    assert seccion.nombre == "Aperitivos"
    assert seccion.nombre_normalizado == "aperitivos"
    assert seccion.subtitulo == "Para compartir"


def test_sec_26_subtitulo_omitido_queda_en_none(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas")
    )

    assert seccion.subtitulo is None


def test_sec_27_actualizar_inexistente_lanza_no_encontrada(sesion):
    with pytest.raises(SeccionNoEncontrada):
        servicios.actualizar_seccion(sesion, 999, SeccionActualizar(nombre="Entradas"))


def test_sec_29_no_encontrada_tiene_prioridad_sobre_duplicado(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas"))

    with pytest.raises(SeccionNoEncontrada):
        servicios.actualizar_seccion(sesion, 999, SeccionActualizar(nombre="Entradas"))


def test_sec_15_duplicado_en_modificacion_no_cambia_la_seccion(
    sesion, crear_seccion, persistir
):
    persistir(crear_seccion(nombre="Entradas"))
    postres_id = persistir(crear_seccion(nombre="Postres", subtitulo="Dulces"))

    with pytest.raises(NombreSeccionDuplicado):
        servicios.actualizar_seccion(
            sesion, postres_id, SeccionActualizar(nombre="entradas", subtitulo="Otro")
        )

    seccion = sesion.get(Seccion, postres_id)
    assert seccion.nombre == "Postres"
    assert seccion.nombre_normalizado == "postres"
    assert seccion.subtitulo == "Dulces"


def test_sec_16_conserva_el_propio_nombre(sesion, crear_seccion, persistir):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", subtitulo="Nuevo")
    )

    assert seccion.subtitulo == "Nuevo"


def test_sec_17_cambio_solo_de_mayusculas_recalcula_el_nombre_normalizado(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas"))

    seccion = servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="ENTRADAS")
    )

    assert seccion.nombre == "ENTRADAS"
    assert seccion.nombre_normalizado == "entradas"


def test_sec_44_subtitulo_de_espacios_se_persiste_como_null(
    sesion, crear_seccion, persistir
):
    seccion_id = persistir(crear_seccion(nombre="Entradas", subtitulo="Para comenzar"))

    servicios.actualizar_seccion(
        sesion, seccion_id, SeccionActualizar(nombre="Entradas", subtitulo="   ")
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
        sesion, seccion_id, SeccionActualizar(nombre="Aperitivos")
    )

    sesion.expire_all()
    assert sesion.get(Plato, plato_id).seccion_id == seccion_id


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

    seccion = servicios.crear_seccion(sesion, SeccionCrear(nombre="Entradas"))

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
