from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

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
    )
    respuesta = ProductoRespuestaBase.model_validate(origen)
    assert respuesta.id == 7
    assert respuesta.dado_de_baja is False
    assert respuesta.nombre == "Milanesa"
