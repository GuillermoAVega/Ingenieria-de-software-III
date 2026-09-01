from datetime import date


def is_valid_date_range(date_from: date | None, date_to: date | None) -> bool:
    if date_from is None or date_to is None:
        return True
    return date_from <= date_to


def matches_dni(dni: int, query: str | None) -> bool:
    if not query:
        return True
    return query.strip() in str(dni)
