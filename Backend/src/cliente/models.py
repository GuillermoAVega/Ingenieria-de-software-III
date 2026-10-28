from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped
from src.models import ModeloBase


class Cliente(ModeloBase):
    __tablename__ = "clientes"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    dni: Mapped[str] = Column(String, unique=True, nullable=False)
    nombre: Mapped[str] = Column(String, nullable=False)
    apellido: Mapped[str] = Column(String, nullable=False)
    telefono: Mapped[str] = Column(String, nullable=False)
    estado: Mapped[bool] = Column(Boolean, nullable=False, default=True)