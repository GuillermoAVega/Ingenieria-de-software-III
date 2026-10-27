from sqlalchemy.orm import Session

from src.productos import services
from src.productos.postres.models import Postre
from src.productos.postres.schemas import PostreActualizar, PostreCrear


def crear_postre(sesion: Session, datos: PostreCrear) -> Postre:
    return services.crear_producto(sesion, Postre, datos)


def actualizar_postre(sesion: Session, postre_id: int, datos: PostreActualizar) -> Postre:
    return services.actualizar_producto(sesion, Postre, postre_id, datos)
