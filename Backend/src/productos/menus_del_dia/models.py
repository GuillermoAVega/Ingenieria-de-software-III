from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from src.productos.constants import TIPO_MENU_DEL_DIA
from src.productos.models import Producto


class MenuDelDia(Producto):
    __tablename__ = "menu_del_dia"
    __mapper_args__ = {"polymorphic_identity": TIPO_MENU_DEL_DIA}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)

    # Referencia a ProductoMenu solo por cadena; sin cascada `delete` (historial)
    fechas = relationship(
        "ProductoMenu",
        back_populates="menu_del_dia",
        order_by="ProductoMenu.fecha",
        foreign_keys="ProductoMenu.menu_del_dia_id",
    )
