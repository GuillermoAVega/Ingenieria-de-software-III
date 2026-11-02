from pydantic import BaseModel, ConfigDict, Field


class MedioPagoCreate(BaseModel):
    descripcion: str = Field(min_length=1, max_length=100)


class MedioPagoUpdate(BaseModel):
    descripcion: str | None = Field(default=None, min_length=1, max_length=100)
    activo: bool | None = None


class MedioPagoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descripcion: str
    activo: bool
