from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, false, text
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase
from src.productos.constants import (
    DESCRIPCION_MAX,
    NOMBRE_MAX,
    PRECIO_DECIMALES,
    PRECIO_DIGITOS,
    TIPO_MAX,
)


class Producto(ModeloBase):
    """Raíz abstracta de la jerarquía (herencia de tablas unidas)."""
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_producto_precio_positivo"),
        # Respaldo de la unicidad entre activos (el servicio verifica primero)
        Index(
            "ux_producto_nombre_activo",
            "nombre_normalizado",
            unique=True,
            sqlite_where=text("dado_de_baja = 0"),
        ),
    )
    __mapper_args__ = {"polymorphic_on": "tipo", "polymorphic_abstract": True}

    id = mapped_column(Integer, primary_key=True)
    tipo = mapped_column(String(TIPO_MAX), nullable=False)
    nombre = mapped_column(String(NOMBRE_MAX), nullable=False)
    nombre_normalizado = mapped_column(String(NOMBRE_MAX), nullable=False)
    precio = mapped_column(
        Numeric(PRECIO_DIGITOS, PRECIO_DECIMALES, asdecimal=True), nullable=False
    )
    descripcion = mapped_column(String(DESCRIPCION_MAX), nullable=True)
    imagen = mapped_column(String, nullable=True)
    dado_de_baja = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    seccion_id = mapped_column(
        ForeignKey("seccion.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Referencia a Seccion solo por cadena; `registro` carga su modelo
    seccion = relationship("Seccion", back_populates="productos")
    # Referencia a ProductoMenu solo por cadena; sin cascada `delete` (historial)
    menus_del_dia = relationship("ProductoMenu", back_populates="producto")

    def __new__(cls, *args, **kw):
        # Se valida en __new__ porque la instrumentación de SQLAlchemy envuelve
        # __init__ y lanzaría InvalidRequestError antes de llegar a nuestro código
        if cls is Producto:
            raise TypeError("Producto es abstracto")
        return super().__new__(cls)
