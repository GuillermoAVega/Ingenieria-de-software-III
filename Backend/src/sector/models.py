from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import ModeloBase

if TYPE_CHECKING:
    from src.atencion.models import Atencion
    from src.mesa.models import Mesa


class Sector(ModeloBase):
    __tablename__ = "sectores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    apto_fumadores: Mapped[bool] = mapped_column(Boolean, default=False)
    piso: Mapped[str] = mapped_column(String(30))
    estado: Mapped[bool] = mapped_column(Boolean, default=True)

    atenciones: Mapped[list["Atencion"]] = relationship(back_populates="sector")
    mesas: Mapped[list["Mesa"]] = relationship(back_populates="sector")