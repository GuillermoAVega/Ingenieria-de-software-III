from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.orm import Mapped

from src.models import ModeloBase


class Mesa(ModeloBase):
    __tablename__ = "mesas"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    capacidad: Mapped[int] = Column(Integer, nullable=False)
    disponible: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    estado: Mapped[bool] = Column(Boolean, nullable=False, default=True)