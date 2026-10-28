from fastapi import HTTPException, status

from src.exceptions import NotFound, BadRequest
from src.sector.constants import ErrorCode


class SectorNoEncontrado(NotFound):
    DETAIL = ErrorCode.SECTOR_NO_ENCONTRADO


class SectorYaInactivo(BadRequest):
    DETAIL = ErrorCode.SECTOR_YA_INACTIVO


class SectorNombreDuplicado(BadRequest):
    DETAIL = ErrorCode.SECTOR_NOMBRE_DUPLICADO


class SectorYaActivo(BadRequest):
    DETAIL = ErrorCode.SECTOR_YA_ACTIVO


class SectorConAtencionesAbiertas(BadRequest):
    DETAIL = ErrorCode.SECTOR_CON_ATENCIONES_ABIERTAS


class SectorConMesasActivas(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=ErrorCode.SECTOR_CON_MESAS_ACTIVAS,
        )
