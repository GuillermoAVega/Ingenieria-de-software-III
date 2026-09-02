import re
import unicodedata

_NAME_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+")
_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+")
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


def normalize_search_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return without_accents.lower()


def matches_search_field(
    normalized_query: str, field: str, *, dni: int, first_name: str, last_name: str
) -> bool:
    if field == "first_name":
        return normalized_query in normalize_search_text(first_name)
    if field == "last_name":
        return normalized_query in normalize_search_text(last_name)
    return normalized_query in str(dni)
