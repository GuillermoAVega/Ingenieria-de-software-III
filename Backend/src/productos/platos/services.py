from datetime import date

from sqlalchemy.orm import Session

from src.productos import services
from src.productos.platos.models import Plato
from src.productos.platos.schemas import PlatoActualizar, PlatoCrear


def listar_platos(sesion: Session) -> list[Plato]:
    return services.listar(sesion, Plato)


def crear_plato(sesion: Session, datos: PlatoCrear) -> Plato:
    return services.crear_producto(
        sesion, Plato, datos, cant_personas=datos.cant_personas
    )


def actualizar_plato(
    sesion: Session, plato_id: int, datos: PlatoActualizar, hoy: date
) -> Plato:
    return services.actualizar_producto(
        sesion, Plato, plato_id, datos, hoy, cant_personas=datos.cant_personas
    )
