from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase
from src.secciones.constants import NOMBRE_MAX, SUBTITULO_MAX


class Seccion(ModeloBase):
    __tablename__ = "seccion"
    __table_args__ = (
        # Única entre todas las secciones: no hay baja lógica que la acote
        Index("ux_seccion_nombre_normalizado", "nombre_normalizado", unique=True),
    )

    id = mapped_column(Integer, primary_key=True)
    nombre = mapped_column(String(NOMBRE_MAX), nullable=False)
    nombre_normalizado = mapped_column(String(NOMBRE_MAX), nullable=False)
    subtitulo = mapped_column(String(SUBTITULO_MAX), nullable=True)

    # Referencia a Producto solo por cadena (secciones no importa productos).
    # La desvinculación al borrar la hace la BD con ON DELETE SET NULL.
    productos = relationship("Producto", back_populates="seccion", passive_deletes=True)
