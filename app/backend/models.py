import enum

from sqlalchemy import Column, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String

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


class ProductStatus(str, enum.Enum):
    ACTIVE = "Activo"
    INACTIVE = "Inactivo"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    description = Column(String, nullable=True)
    unit_price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    status = Column(SqlEnum(ProductStatus), nullable=False)


class SaleStatus(str, enum.Enum):
    CONFIRMED = "Confirmada"
    CANCELLED = "Anulada"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(SqlEnum(SaleStatus), nullable=False)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
