from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship

from src.productos.constants import TIPO_PLATO
from src.productos.models import Producto
from src.productos.platos.constants import CANT_PERSONAS_MIN


class Plato(Producto):
    __tablename__ = "plato"
    __table_args__ = (
        CheckConstraint(
            f"cant_personas >= {CANT_PERSONAS_MIN}", name="ck_plato_cant_personas_minima"
        ),
    )
    __mapper_args__ = {"polymorphic_identity": TIPO_PLATO}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cant_personas = mapped_column(Integer, nullable=False)

    # Referencias a otros subtipos solo por cadena (sin importar sus subpaquetes)
    menus = relationship(
        "MenuEjecutivo", foreign_keys="MenuEjecutivo.plato_id", back_populates="plato"
    )
    combos = relationship("ComboPromocion", secondary="combo_plato", back_populates="platos")
