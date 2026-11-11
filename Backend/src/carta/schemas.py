from pydantic import BaseModel

from src.productos.bebidas.schemas import BebidaRespuesta
from src.productos.combos.schemas import ComboRespuesta
from src.productos.menus_del_dia.schemas import MenuDelDiaListado
from src.productos.menus_ejecutivos.schemas import MenuRespuesta
from src.productos.platos.schemas import PlatoRespuesta
from src.productos.postres.schemas import PostreRespuesta
from src.productos_menu.schemas import ProductoMenuDetalleRespuesta
from src.promociones.schemas import PromocionRespuesta
from src.secciones.schemas import SeccionRespuesta


class CartaRespuesta(BaseModel):
    menus_diarios: list[ProductoMenuDetalleRespuesta]
    menus_del_dia: list[MenuDelDiaListado]
    menus_ejecutivos: list[MenuRespuesta]
    combos: list[ComboRespuesta]
    platos: list[PlatoRespuesta]
    postres: list[PostreRespuesta]
    bebidas: list[BebidaRespuesta]
    secciones: list[SeccionRespuesta]
    promociones: list[PromocionRespuesta]
