from sqlalchemy import Date, ForeignKey, Index, Integer
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase


class ProductoMenu(ModeloBase):
    __tablename__ = "producto_menu"
    __table_args__ = (
        # Un solo menú del día por fecha; el servicio verifica primero
        Index("ux_producto_menu_fecha", "fecha", unique=True),
    )

    id = mapped_column(Integer, primary_key=True)
    # FK por cadena (sin ON DELETE): este módulo no importa productos
    producto_id = mapped_column(ForeignKey("producto.id"), nullable=False, index=True)
    fecha = mapped_column(Date, nullable=False)

    # Referencia a Producto solo por cadena; `registro` carga su modelo
    producto = relationship("Producto", back_populates="menus_del_dia")
