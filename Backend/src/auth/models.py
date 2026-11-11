from enum import Enum

from sqlalchemy import Boolean, Enum as SqlEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import ModeloBase


class RolUsuario(str, Enum):
    ADMINISTRADOR = "administrador"
    OPERARIO = "operario"


class Usuario(ModeloBase):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre_usuario: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    clave_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        SqlEnum(RolUsuario, native_enum=False), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
