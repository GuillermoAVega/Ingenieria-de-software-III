from src.exceptions import NotFound, BadRequest
from src.mozo.constants import ErrorCode


class MozoNoEncontrado(NotFound):
    DETAIL = ErrorCode.MOZO_NO_ENCONTRADO


class LegajoDuplicado(BadRequest):
    DETAIL = ErrorCode.MOZO_LEGAJO_DUPLICADO


class MozoYaInactivo(BadRequest):
    DETAIL = ErrorCode.MOZO_YA_INACTIVO


class MozoYaActivo(BadRequest):
    DETAIL = ErrorCode.MOZO_YA_ACTIVO


class MozoConAtencionesAbiertas(BadRequest):
    DETAIL = ErrorCode.MOZO_CON_ATENCIONES_ABIERTAS
