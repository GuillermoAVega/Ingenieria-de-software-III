from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from src.productos.constants import TIPO_POSTRE
from src.productos.models import Producto


class Postre(Producto):
    __tablename__ = "postre"
    __mapper_args__ = {"polymorphic_identity": TIPO_POSTRE}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)

    menus = relationship(
        "MenuEjecutivo", foreign_keys="MenuEjecutivo.postre_id", back_populates="postre"
    )
    combos = relationship("ComboPromocion", secondary="combo_postre", back_populates="postres")
