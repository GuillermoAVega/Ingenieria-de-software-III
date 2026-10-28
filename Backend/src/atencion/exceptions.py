from src.exceptions import NotFound, BadRequest
from src.atencion.constants import ErrorCode


class AtencionNoEncontrada(NotFound):
    DETAIL = ErrorCode.ATENCION_NO_ENCONTRADA


class AtencionYaInactiva(BadRequest):
    DETAIL = ErrorCode.ATENCION_YA_INACTIVA


class FechaInvalida(BadRequest):
    DETAIL = ErrorCode.ATENCION_FECHA_INVALIDA


class MozoInvalido(BadRequest):
    DETAIL = ErrorCode.MOZO_INACTIVO_O_INEXISTENTE


class SectorInvalido(BadRequest):
    DETAIL = ErrorCode.SECTOR_INACTIVO_O_INEXISTENTE
