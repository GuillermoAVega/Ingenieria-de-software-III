from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from src.productos.constants import TIPO_MENU_EJECUTIVO
from src.productos.models import Producto


class MenuEjecutivo(Producto):
    __tablename__ = "menu_ejecutivo"
    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    plato_id = mapped_column(ForeignKey("plato.id"), nullable=False)
    postre_id = mapped_column(ForeignKey("postre.id"), nullable=False)

    # Hay varias FK hacia la jerarquía: se explicita cuál une con `producto`
    __mapper_args__ = {
        "polymorphic_identity": TIPO_MENU_EJECUTIVO,
        "inherit_condition": id == Producto.id,
    }

    # Referencias a otros subtipos solo por cadena (sin importar sus subpaquetes)
    plato = relationship("Plato", foreign_keys=[plato_id], back_populates="menus")
    postre = relationship("Postre", foreign_keys=[postre_id], back_populates="menus")
