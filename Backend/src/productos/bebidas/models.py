from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from src.productos.constants import TIPO_BEBIDA
from src.productos.models import Producto


class Bebida(Producto):
    __tablename__ = "bebida"
    __mapper_args__ = {"polymorphic_identity": TIPO_BEBIDA}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    es_alcoholica = mapped_column(Boolean, nullable=False)

    combos = relationship("ComboPromocion", secondary="combo_bebida", back_populates="bebidas")
