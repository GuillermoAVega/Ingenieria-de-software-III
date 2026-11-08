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
    menu_del_dia_id = mapped_column(
        ForeignKey("menu_del_dia.id"), nullable=False, index=True
    )
    fecha = mapped_column(Date, nullable=False)

    # Referencia a MenuDelDia solo por cadena; `registro` carga su modelo
    menu_del_dia = relationship("MenuDelDia", back_populates="fechas")
