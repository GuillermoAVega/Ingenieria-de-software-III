from app.backend import core


def validate_positive_number(value: str) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def validate_positive_integer(value: str) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


ACTIVE_STATUS = "Activo"


def initial_status() -> str:
    return ACTIVE_STATUS


def matches_search(normalized_query: str, *, sku: str, name: str) -> bool:
    if normalized_query in core.normalize_search_text(name):
        return True
    return normalized_query in core.normalize_search_text(sku)


def matches_venta_search(
    normalized_query: str, *, name: str, description: str | None
) -> bool:
    if normalized_query in core.normalize_search_text(name):
        return True
    if not description:
        return False
    return normalized_query in core.normalize_search_text(description)
