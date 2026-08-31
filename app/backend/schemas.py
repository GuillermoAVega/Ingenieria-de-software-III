from pydantic import BaseModel


class ClienteAltaRequest(BaseModel):
    dni: str
    first_name: str
    last_name: str
    email: str
    phone: str
