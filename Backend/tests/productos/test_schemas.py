from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.productos.bebidas.schemas import (
    BebidaActualizar,
    BebidaCrear,
    BebidaRespuesta,
)
from src.productos.combos.schemas import ComboActualizar, ComboCrear, ComboRespuesta
from src.productos.menus_ejecutivos.schemas import (
    MenuActualizar,
    MenuCrear,
    MenuRespuesta,
)
from src.productos.platos.schemas import PlatoActualizar, PlatoCrear, PlatoRespuesta
from src.productos.postres.schemas import (
    PostreActualizar,
    PostreCrear,
    PostreRespuesta,
)
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


def crear_base(**cambios):
    datos = {"nombre": "Milanesa", "precio": "1500.50"}
    datos.update(cambios)
    return ProductoBase(**datos)


# --- 2.2 ProductoBase ---


def test_nombre_vacio_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(nombre="")


def test_nombre_solo_espacios_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(nombre="   ")


def test_nombre_se_recorta():
    assert crear_base(nombre="  Milanesa ").nombre == "Milanesa"


def test_nombre_de_100_caracteres_es_valido_y_de_101_se_rechaza():
    assert len(crear_base(nombre="a" * 100).nombre) == 100
    with pytest.raises(ValidationError):
        crear_base(nombre="a" * 101)


def test_nombre_de_100_caracteres_con_espacios_se_valida_tras_el_recorte():
    assert crear_base(nombre=" " + "a" * 100 + " ").nombre == "a" * 100


def test_precio_cero_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(precio="0")


def test_precio_negativo_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(precio="-1.00")


def test_precio_con_mas_de_dos_decimales_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(precio="10.123")


def test_precio_con_mas_de_diez_digitos_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(precio="123456789.01")


def test_precio_valido_es_decimal():
    assert crear_base(precio="99999999.99").precio == Decimal("99999999.99")


def test_descripcion_de_500_es_valida_y_de_501_se_rechaza():
    assert len(crear_base(descripcion="a" * 500).descripcion) == 500
    with pytest.raises(ValidationError):
        crear_base(descripcion="a" * 501)


def test_descripcion_e_imagen_son_opcionales():
    producto = crear_base()
    assert producto.descripcion is None
    assert producto.imagen is None


def test_respuesta_base_se_construye_desde_atributos():
    origen = SimpleNamespace(
        id=7,
        nombre="Milanesa",
        precio=Decimal("1500.50"),
        descripcion=None,
        imagen=None,
        dado_de_baja=False,
        seccion_id=None,
    )
    respuesta = ProductoRespuestaBase.model_validate(origen)
    assert respuesta.id == 7
    assert respuesta.dado_de_baja is False
    assert respuesta.nombre == "Milanesa"


# --- 2.2 seccion_id ---


def test_cat_s_02_seccion_id_omitido_queda_en_none():
    assert crear_base().seccion_id is None


def test_seccion_id_entero_se_conserva():
    assert crear_base(seccion_id=2).seccion_id == 2


def test_cat_s_13_seccion_id_de_tipo_invalido_se_rechaza():
    with pytest.raises(ValidationError):
        crear_base(seccion_id="abc")


@pytest.mark.parametrize("seccion_id", [None, 2])
def test_respuesta_base_expone_seccion_id(seccion_id):
    origen = SimpleNamespace(
        id=7,
        nombre="Milanesa",
        precio=Decimal("1500.50"),
        descripcion=None,
        imagen=None,
        dado_de_baja=False,
        seccion_id=seccion_id,
    )
    assert ProductoRespuestaBase.model_validate(origen).seccion_id == seccion_id


@pytest.mark.parametrize(
    "esquema",
    [
        PlatoCrear, PlatoActualizar, PlatoRespuesta,
        BebidaCrear, BebidaActualizar, BebidaRespuesta,
        PostreCrear, PostreActualizar, PostreRespuesta,
        MenuCrear, MenuActualizar, MenuRespuesta,
        ComboCrear, ComboActualizar, ComboRespuesta,
    ],
)
def test_los_subtipos_heredan_seccion_id(esquema):
    assert "seccion_id" in esquema.model_fields


# --- PMD-39 [CARACTERIZACIÓN: nace en verde] ---


@pytest.mark.parametrize(
    "esquema",
    [
        PlatoRespuesta,
        BebidaRespuesta,
        PostreRespuesta,
        MenuRespuesta,
        ComboRespuesta,
        ProductoRespuestaBase,
    ],
)
def test_pmd_39_respuestas_de_producto_no_exponen_menus_del_dia(esquema):
    assert "menus_del_dia" not in esquema.model_fields
