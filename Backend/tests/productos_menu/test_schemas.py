from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.productos_menu.schemas import (
    ProductoMenuActualizar,
    ProductoMenuCrear,
    ProductoMenuRespuesta,
)


def test_pmd_09_producto_id_ausente_se_rechaza():
    with pytest.raises(ValidationError):
        ProductoMenuCrear(fecha="2026-06-15")


def test_pmd_10_producto_id_no_entero_se_rechaza():
    with pytest.raises(ValidationError):
        ProductoMenuCrear(producto_id="abc", fecha="2026-06-15")


def test_pmd_11_fecha_ausente_se_rechaza():
    with pytest.raises(ValidationError):
        ProductoMenuCrear(producto_id=1)


@pytest.mark.parametrize("fecha", ["no-es-una-fecha", "2026-02-30"])
def test_pmd_12_fecha_invalida_se_rechaza(fecha):
    with pytest.raises(ValidationError):
        ProductoMenuCrear(producto_id=1, fecha=fecha)


@pytest.mark.parametrize(
    "fecha",
    [date(2000, 1, 1), date.today(), date(2100, 1, 1)],
    ids=["pasada", "hoy", "futura"],
)
def test_pmd_05_06_07_fechas_pasada_hoy_y_futura_son_validas(fecha):
    assert ProductoMenuCrear(producto_id=1, fecha=fecha).fecha == fecha


def test_fecha_iso_se_parsea_a_date():
    datos = ProductoMenuCrear(producto_id=1, fecha="2026-10-28")
    assert datos.fecha == date(2026, 10, 28)
    assert isinstance(datos.fecha, date)


@pytest.mark.parametrize("cuerpo", [{}, {"fecha": "no-es-una-fecha"}, {"fecha": "2026-02-30"}])
def test_pmd_27_actualizar_fecha_ausente_o_invalida_se_rechaza(cuerpo):
    with pytest.raises(ValidationError):
        ProductoMenuActualizar(**cuerpo)


def test_pmd_26_actualizar_ignora_producto_id():
    datos = ProductoMenuActualizar(fecha="2026-06-15", producto_id=7)
    assert datos.model_dump() == {"fecha": date(2026, 6, 15)}


def test_pmd_03_respuesta_expone_solo_id_producto_id_y_fecha():
    assert set(ProductoMenuRespuesta.model_fields) == {"id", "producto_id", "fecha"}
    assert ProductoMenuRespuesta.model_config["from_attributes"] is True


def test_respuesta_se_construye_desde_atributos():
    origen = SimpleNamespace(id=1, producto_id=2, fecha=date(2026, 6, 15), extra="x")
    assert ProductoMenuRespuesta.model_validate(origen).model_dump() == {
        "id": 1,
        "producto_id": 2,
        "fecha": date(2026, 6, 15),
    }
