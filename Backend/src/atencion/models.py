from typing import TYPE_CHECKING

from datetime import date
from sqlalchemy import Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import ModeloBase

if TYPE_CHECKING:
    from src.mozo.models import Mozo
    from src.sector.models import Sector


class Atencion(ModeloBase):
    __tablename__ = "atenciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    fecha_desde: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    mozo_id: Mapped[int] = mapped_column(Integer, ForeignKey("mozos.id"), nullable=False)
    sector_id: Mapped[int] = mapped_column(Integer, ForeignKey("sectores.id"), nullable=False)
    estado: Mapped[bool] = mapped_column(Boolean, default=True)

    mozo: Mapped["Mozo"] = relationship(back_populates="atenciones")
    sector: Mapped["Sector"] = relationship(back_populates="atenciones")
