from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import ModeloBase

if TYPE_CHECKING:
    from src.sector.models import Sector


class Mesa(ModeloBase):
    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    estado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sector_id: Mapped[int] = mapped_column(
        ForeignKey("sectores.id"),
        nullable=False,
    )

    sector: Mapped["Sector"] = relationship(back_populates="mesas")