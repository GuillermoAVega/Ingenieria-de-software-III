from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase
from src.productos.constants import TIPO_COMBO_PROMOCION
from src.productos.models import Producto

def _componente_combo(nombre: str, tipo: str, tabla_componente: str):
    """Fabrica la clase de asociación combo-componente con su `cantidad` (CHECK >= 1)."""
    columna = f"{tipo}_id"
    atributos = {
        "__tablename__": nombre,
        "__table_args__": (
            CheckConstraint("cantidad >= 1", name=f"ck_{nombre}_cantidad_minima"),
        ),
        "combo_id": mapped_column(ForeignKey("combo_promocion.id"), primary_key=True),
        columna: mapped_column(ForeignKey(f"{tabla_componente}.id"), primary_key=True),
        "cantidad": mapped_column(Integer, nullable=False, server_default="1"),
        tipo: relationship(tipo.capitalize()),
    }
    return type(f"Combo{tipo.capitalize()}", (ModeloBase,), atributos)


# Asociaciones del combo con sus componentes (la PK compuesta impide duplicados)
ComboPlato = _componente_combo("combo_plato", "plato", "plato")
ComboBebida = _componente_combo("combo_bebida", "bebida", "bebida")
ComboPostre = _componente_combo("combo_postre", "postre", "postre")

# Alias de tabla: `RESTRICT_POR_TIPO` y `buscar_bloqueantes` consultan `.c.<columna>`
combo_plato = ComboPlato.__table__
combo_bebida = ComboBebida.__table__
combo_postre = ComboPostre.__table__


class ComboPromocion(Producto):
    __tablename__ = "combo_promocion"
    __table_args__ = (
        CheckConstraint("fecha_desde <= fecha_hasta", name="ck_combo_rango_de_fechas"),
    )
    __mapper_args__ = {"polymorphic_identity": TIPO_COMBO_PROMOCION}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    fecha_desde = mapped_column(Date, nullable=False)
    fecha_hasta = mapped_column(Date, nullable=False)

    # Referencias a otros subtipos solo por cadena (sin importar sus subpaquetes)
    componentes_platos = relationship(
        "ComboPlato", cascade="all, delete-orphan", order_by="ComboPlato.plato_id"
    )
    componentes_bebidas = relationship(
        "ComboBebida", cascade="all, delete-orphan", order_by="ComboBebida.bebida_id"
    )
    componentes_postres = relationship(
        "ComboPostre", cascade="all, delete-orphan", order_by="ComboPostre.postre_id"
    )

    # Listas `[{"id", "cantidad"}]` ordenadas por id, pensadas para serializar con from_attributes
    @property
    def platos(self):
        return self._componentes(self.componentes_platos, "plato_id")

    @property
    def bebidas(self):
        return self._componentes(self.componentes_bebidas, "bebida_id")

    @property
    def postres(self):
        return self._componentes(self.componentes_postres, "postre_id")

    @staticmethod
    def _componentes(asociaciones, columna: str):
        return sorted(
            ({"id": getattr(a, columna), "cantidad": a.cantidad} for a in asociaciones),
            key=lambda componente: componente["id"],
        )
