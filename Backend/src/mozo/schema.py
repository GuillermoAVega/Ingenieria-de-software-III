from pydantic import BaseModel, Field, field_validator
from typing import Optional


class MozoBase(BaseModel):
    nombre: str = Field(max_length=50, description="Nombre del mozo (máximo 50 caracteres)")
    nro_legajo: int = Field(gt=0, description="Número de legajo del mozo (entero positivo)")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if len(v) > 50:
            raise ValueError("El nombre no debe superar los 50 caracteres.")
        return v.strip()


class MozoCreate(MozoBase):
    pass


class MozoUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, max_length=50)
    nro_legajo: Optional[int] = Field(default=None, gt=0)

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


class Mozo(MozoBase):
    id: int
    estado: bool

    model_config = {"from_attributes": True}
