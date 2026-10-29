from pydantic import BaseModel, EmailStr, field_validator
import re
import unicodedata


class ClienteBase(BaseModel):
    dni: str
    nombre: str
    apellido: str
    telefono: str

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre_apellido(cls, valor: str) -> str:
        valor = unicodedata.normalize("NFC", valor).strip()
        if not valor or not all(palabra.isalpha() for palabra in valor.split()):
            raise ValueError("Nombre y apellido solo deben contener letras")
        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor):
        if not re.fullmatch(r"[0-9-]+", valor):
            raise ValueError("El formato del teléfono es incorrecto")
        return valor


class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass


class Cliente(ClienteBase):
    id: int
    estado: bool

    model_config = {
        "from_attributes": True
    }