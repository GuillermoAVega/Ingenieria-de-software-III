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
