from pydantic import BaseModel


class DetalleReservaBase(BaseModel):
    producto_id: int
    cantidad_producto: int


class DetalleReservaCreate(DetalleReservaBase):
    pass


class DetalleReserva(DetalleReservaBase):
    reserva_id: int

    model_config = {
        "from_attributes": True
    }