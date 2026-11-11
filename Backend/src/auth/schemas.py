from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.auth.models import RolUsuario


class CredencialesLogin(BaseModel):
    nombre_usuario: str = Field(min_length=1, max_length=50)
    clave: str = Field(min_length=1, max_length=128)


class UsuarioCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    nombre_usuario: str = Field(min_length=3, max_length=50)
    clave: str = Field(min_length=8, max_length=128)
    rol: RolUsuario

    @field_validator("nombre", "nombre_usuario", mode="before")
    @classmethod
    def quitar_espacios(cls, valor: str) -> str:
        return valor.strip()


class UsuarioActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    nombre_usuario: str | None = Field(default=None, min_length=3, max_length=50)
    clave: str | None = Field(default=None, min_length=8, max_length=128)
    rol: RolUsuario | None = None
    activo: bool | None = None

    @field_validator("nombre", "nombre_usuario", mode="before")
    @classmethod
    def quitar_espacios(cls, valor: str | None) -> str | None:
        return valor.strip() if valor is not None else None


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    nombre_usuario: str
    rol: RolUsuario
    activo: bool


class SesionRespuesta(BaseModel):
    token: str
    tipo: str = "bearer"
    usuario: UsuarioRespuesta
