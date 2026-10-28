from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SectorBase(BaseModel):
    nombre: str = Field(max_length=50, description="Nombre del sector (máximo 50 caracteres)")
    apto_fumadores: bool = Field(description="Indica si el sector es apto para fumadores")
    piso: int = Field(description="Piso del sector (entero)")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 50:
            raise ValueError("El nombre no debe superar los 50 caracteres.")
        return v.strip()


class SectorCreate(SectorBase):
    pass


class SectorUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    nombre: Optional[str] = Field(default=None, max_length=50)
    apto_fumadores: Optional[bool] = None
    piso: Optional[int] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 50:
            raise ValueError("El nombre no debe superar los 50 caracteres.")
        return v.strip()


class Sector(SectorBase):
    id: int
    estado: bool

    model_config = {"from_attributes": True}
