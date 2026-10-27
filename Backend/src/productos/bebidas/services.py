from sqlalchemy.orm import Session

from src.productos import services
from src.productos.bebidas.models import Bebida
from src.productos.bebidas.schemas import BebidaActualizar, BebidaCrear


def crear_bebida(sesion: Session, datos: BebidaCrear) -> Bebida:
    return services.crear_producto(
        sesion, Bebida, datos, es_alcoholica=datos.es_alcoholica
    )


def actualizar_bebida(sesion: Session, bebida_id: int, datos: BebidaActualizar) -> Bebida:
    return services.actualizar_producto(
        sesion, Bebida, bebida_id, datos, es_alcoholica=datos.es_alcoholica
    )
