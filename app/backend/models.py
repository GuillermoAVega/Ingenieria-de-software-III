import enum

from sqlalchemy import Column, Enum as SqlEnum, Integer, String

from app.backend.database import Base


class ClientStatus(str, enum.Enum):
    ACTIVE = "Activo"
    INACTIVE = "Inactivo"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(Integer, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    status = Column(SqlEnum(ClientStatus), nullable=False, default=ClientStatus.ACTIVE)
