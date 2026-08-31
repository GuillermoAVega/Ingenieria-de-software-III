from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.backend import core, repository
from app.backend.database import get_session

router = APIRouter()

SUCCESS_MESSAGE = "Cliente registrado exitosamente"
REQUIRED_FIELD_MESSAGE = "El campo es obligatorio"
INVALID_NAME_MESSAGE = "El campo solo debe contener letras"
INVALID_EMAIL_MESSAGE = "El email es inválido"
INVALID_PHONE_MESSAGE = "El formato del teléfono es incorrecto"
INVALID_DNI_MESSAGE = "El formato del DNI es inválido"
DUPLICATE_DNI_MESSAGE = "El cliente ya se encuentra registrado"

_REQUIRED_FIELDS = ("dni", "first_name", "last_name", "email", "phone")


def _normalize_payload(payload: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for field in _REQUIRED_FIELDS:
        raw_value = payload.get(field)
        value = raw_value if isinstance(raw_value, str) else ""
        normalized[field] = core.trim_leading_trailing_space(value)
    return normalized


def _validate_fields(values: dict[str, str]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    for field in _REQUIRED_FIELDS:
        if not values[field]:
            errors.append({"field": field, "message": REQUIRED_FIELD_MESSAGE})

    if values["first_name"] and not core.validate_name(values["first_name"]):
        errors.append({"field": "first_name", "message": INVALID_NAME_MESSAGE})
    if values["last_name"] and not core.validate_name(values["last_name"]):
        errors.append({"field": "last_name", "message": INVALID_NAME_MESSAGE})
    if values["email"] and not core.validate_email(values["email"]):
        errors.append({"field": "email", "message": INVALID_EMAIL_MESSAGE})
    if values["phone"] and not core.validate_phone(values["phone"]):
        errors.append({"field": "phone", "message": INVALID_PHONE_MESSAGE})
    if values["dni"] and not core.validate_dni_format(values["dni"]):
        errors.append({"field": "dni", "message": INVALID_DNI_MESSAGE})

    return errors


@router.post("/clientes")
def alta_cliente(
    payload: dict[str, Any], session: Session = Depends(get_session)
) -> JSONResponse:
    values = _normalize_payload(payload)
    errors = _validate_fields(values)

    if errors:
        return JSONResponse(status_code=422, content={"errors": errors})

    if repository.dni_exists(session, values["dni"]):
        return JSONResponse(
            status_code=422,
            content={"errors": [{"field": "dni", "message": DUPLICATE_DNI_MESSAGE}]},
        )

    customer = repository.create_customer(
        session,
        dni=values["dni"],
        first_name=values["first_name"],
        last_name=values["last_name"],
        email=values["email"],
        phone=values["phone"],
    )

    return JSONResponse(
        status_code=201,
        content={
            "message": SUCCESS_MESSAGE,
            "customer": {
                "dni": customer.dni,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "phone": customer.phone,
                "status": customer.status.value,
            },
        },
    )
