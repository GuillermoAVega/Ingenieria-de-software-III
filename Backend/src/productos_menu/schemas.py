from datetime import date

from pydantic import AliasPath, BaseModel, ConfigDict, Field


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


class ProductoMenuDetalleRespuesta(BaseModel):
    """Ítem de listado/consulta: incluye el producto asociado ya resuelto.

    Es exclusivo de los `GET`; el alta y la modificación conservan
    `ProductoMenuRespuesta` (`id`, `producto_id`, `fecha`).
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    fecha: date
    producto_nombre: str = Field(validation_alias=AliasPath("producto", "nombre"))
    producto_tipo: str = Field(validation_alias=AliasPath("producto", "tipo"))
    producto_dado_de_baja: bool = Field(
        validation_alias=AliasPath("producto", "dado_de_baja")
    )
