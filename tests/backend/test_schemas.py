import pytest
from pydantic import ValidationError

from app.backend.schemas import ClienteAltaRequest


def test_falta_campo_obligatorio_dni():
    with pytest.raises(ValidationError) as exc_info:
        ClienteAltaRequest(
            first_name="Juan",
            last_name="Perez",
            email="juan@dominio.com",
            phone="11-4444-5555",
        )
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("dni",) for error in errors)


def test_falta_campo_obligatorio_email():
    with pytest.raises(ValidationError) as exc_info:
        ClienteAltaRequest(
            dni="30111222",
            first_name="Juan",
            last_name="Perez",
            phone="11-4444-5555",
        )
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("email",) for error in errors)


def test_payload_completo_es_valido():
    payload = ClienteAltaRequest(
        dni="30111222",
        first_name="Juan",
        last_name="Perez",
        email="juan@dominio.com",
        phone="11-4444-5555",
    )
    assert payload.dni == "30111222"
