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
