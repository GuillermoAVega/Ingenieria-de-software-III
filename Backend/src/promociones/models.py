from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    false,
)
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase
from src.promociones.constants import DESCUENTO_DECIMALES, DESCUENTO_DIGITOS, NOMBRE_MAX

# Asociación N:M con Producto (la PK compuesta impide duplicados)
promocion_producto = Table(
    "promocion_producto",
    ModeloBase.metadata,
    Column("promocion_id", ForeignKey("promocion.id"), primary_key=True),
    Column("producto_id", ForeignKey("producto.id"), primary_key=True),
)


class Promocion(ModeloBase):
    __tablename__ = "promocion"
    __table_args__ = (
        CheckConstraint("fecha_desde <= fecha_hasta", name="ck_promocion_rango_de_fechas"),
        CheckConstraint(
            "tipo IN ('porcentaje', 'lleva_paga')", name="ck_promocion_tipo"
        ),
        CheckConstraint(
            "(tipo = 'porcentaje' AND descuento IS NOT NULL AND descuento > 0"
            " AND descuento <= 100 AND lleva IS NULL AND paga IS NULL)"
            " OR (tipo = 'lleva_paga' AND descuento IS NULL AND lleva IS NOT NULL"
            " AND paga IS NOT NULL AND paga >= 1 AND lleva > paga)",
            name="ck_promocion_parametros",
        ),
    )

    id = mapped_column(Integer, primary_key=True)
    nombre = mapped_column(String(NOMBRE_MAX), nullable=False)
    tipo = mapped_column(String(20), nullable=False)
    fecha_desde = mapped_column(Date, nullable=False)
    fecha_hasta = mapped_column(Date, nullable=False)
    descuento = mapped_column(
        Numeric(DESCUENTO_DIGITOS, DESCUENTO_DECIMALES, asdecimal=True), nullable=True
    )
    lleva = mapped_column(Integer, nullable=True)
    paga = mapped_column(Integer, nullable=True)
    dado_de_baja = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    # Referencia a Producto solo por cadena (`registro` carga sus mappers)
    productos = relationship("Producto", secondary=promocion_producto)

    @property
    def productos_ids(self):
        """Ids de los productos asociados, ascendentes (para from_attributes)."""
        return sorted(producto.id for producto in self.productos)
