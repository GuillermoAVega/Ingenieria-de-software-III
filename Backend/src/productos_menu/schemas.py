from datetime import date

from pydantic import BaseModel, ConfigDict


class ProductoMenuCrear(BaseModel):
    # `producto_id` y `fecha` laxos, como `seccion_id` y `fecha_desde`
    producto_id: int
    fecha: date


class ProductoMenuActualizar(BaseModel):
    # Solo la fecha: cualquier otro campo (p. ej. `producto_id`) se ignora
    fecha: date


class ProductoMenuRespuesta(BaseModel):
    """Respuesta de un menú del día; se construye desde el modelo ORM."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    fecha: date
