from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import ModeloBase

if TYPE_CHECKING:
    from src.atencion.models import Atencion


class Mozo(ModeloBase):
    __tablename__ = "mozos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), index=True)
    nro_legajo: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    estado: Mapped[bool] = mapped_column(Boolean, default=True)

    atenciones: Mapped[list["Atencion"]] = relationship(back_populates="mozo")

    # [TODO] incorporar relacion de mozo con comanda