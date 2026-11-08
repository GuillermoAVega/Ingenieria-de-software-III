from datetime import date

from pydantic import AliasPath, BaseModel, ConfigDict, Field


class ProductoMenuCrear(BaseModel):
    # `menu_del_dia_id` y `fecha` laxos, como `seccion_id` y `fecha_desde`
    menu_del_dia_id: int
    fecha: date


class ProductoMenuActualizar(BaseModel):
    # Solo la fecha: cualquier otro campo (p. ej. `menu_del_dia_id`) se ignora
    fecha: date


class ProductoMenuRespuesta(BaseModel):
    """Respuesta de un menú del día; se construye desde el modelo ORM."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_del_dia_id: int
    fecha: date


class ProductoMenuDetalleRespuesta(BaseModel):
    """Ítem de listado/consulta: incluye el producto asociado ya resuelto.

    Es exclusivo de los `GET`; el alta y la modificación conservan
    `ProductoMenuRespuesta` (`id`, `menu_del_dia_id`, `fecha`).
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_del_dia_id: int
    fecha: date
    menu_del_dia_nombre: str = Field(validation_alias=AliasPath("menu_del_dia", "nombre"))
    menu_del_dia_dado_de_baja: bool = Field(
        validation_alias=AliasPath("menu_del_dia", "dado_de_baja")
    )
