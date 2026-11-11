from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.carta import services
from src.carta.schemas import CartaRespuesta
from src.database import get_db
from src.productos.services import obtener_hoy

router = APIRouter(prefix="/carta", tags=["Carta"])


@router.get("", response_model=CartaRespuesta)
def obtener_carta(
    sesion: Session = Depends(get_db),
    hoy: date = Depends(obtener_hoy),
):
    return services.obtener_carta(sesion, hoy)
