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
