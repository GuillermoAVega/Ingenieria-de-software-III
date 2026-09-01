import re

_NAME_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+")
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_PHONE_PATTERN = re.compile(r"[0-9-]+")
_DNI_FORMAT_PATTERN = re.compile(r"\d{7,8}")

ACTIVE_STATUS = "Activo"


def validate_name(value: str) -> bool:
    return bool(_NAME_PATTERN.fullmatch(value))


def validate_email(value: str) -> bool:
    return bool(_EMAIL_PATTERN.fullmatch(value))


def validate_phone(value: str) -> bool:
    return bool(_PHONE_PATTERN.fullmatch(value))


def validate_dni_format(value: str) -> bool:
    return bool(_DNI_FORMAT_PATTERN.fullmatch(value))


def trim_leading_trailing_space(value: str) -> str:
    return value.strip(" ")


def normalize_dni(value: str) -> int:
    return int(value)


def try_normalize_dni(value: str) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def initial_status() -> str:
    return ACTIVE_STATUS
