from datetime import date
from typing import Literal

from pydantic import model_validator

from src.productos.constants import TIPO_COMBO_PROMOCION
from src.productos.schemas import ProductoBase, ProductoRespuestaBase


class ComboCrear(ProductoBase):
    fecha_desde: date
    fecha_hasta: date
    platos_ids: list[int] = []
    bebidas_ids: list[int] = []
    postres_ids: list[int] = []

    @model_validator(mode="after")
    def validar_combo(self):
        if self.fecha_desde > self.fecha_hasta:
            raise ValueError("fecha_desde no puede ser posterior a fecha_hasta")
        listas = (self.platos_ids, self.bebidas_ids, self.postres_ids)
        if not any(listas):
            raise ValueError("El combo necesita al menos un componente")
        if any(len(lista) != len(set(lista)) for lista in listas):
            raise ValueError("Los ids de componentes no pueden repetirse")
        return self


class ComboActualizar(ComboCrear):
    # Omitido (None) conserva el estado actual
    dado_de_baja: bool | None = None


class ComboRespuesta(ProductoRespuestaBase):
    tipo: Literal[TIPO_COMBO_PROMOCION]
    fecha_desde: date
    fecha_hasta: date
    platos_ids: list[int]
    bebidas_ids: list[int]
    postres_ids: list[int]
