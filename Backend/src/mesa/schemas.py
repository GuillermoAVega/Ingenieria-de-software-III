from pydantic import BaseModel


class MesaBase(BaseModel):
    capacidad: int
    disponible: bool


class MesaCreate(MesaBase):
    pass


class MesaUpdate(MesaBase):
    pass


class Mesa(MesaBase):
    id: int
    estado: bool

    model_config = {
        "from_attributes": True
    }