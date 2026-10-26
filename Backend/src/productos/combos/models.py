from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Table
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase
from src.productos.constants import TIPO_COMBO_PROMOCION
from src.productos.models import Producto

# Tablas de asociación del combo con sus componentes (la PK compuesta impide duplicados)
combo_plato = Table(
    "combo_plato",
    ModeloBase.metadata,
    Column("combo_id", ForeignKey("combo_promocion.id"), primary_key=True),
    Column("plato_id", ForeignKey("plato.id"), primary_key=True),
)
combo_bebida = Table(
    "combo_bebida",
    ModeloBase.metadata,
    Column("combo_id", ForeignKey("combo_promocion.id"), primary_key=True),
    Column("bebida_id", ForeignKey("bebida.id"), primary_key=True),
)
combo_postre = Table(
    "combo_postre",
    ModeloBase.metadata,
    Column("combo_id", ForeignKey("combo_promocion.id"), primary_key=True),
    Column("postre_id", ForeignKey("postre.id"), primary_key=True),
)


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
    platos = relationship("Plato", secondary=combo_plato, back_populates="combos")
    bebidas = relationship("Bebida", secondary=combo_bebida, back_populates="combos")
    postres = relationship("Postre", secondary=combo_postre, back_populates="combos")

    # Listas ordenadas de ids, pensadas para serializar con from_attributes
    @property
    def platos_ids(self):
        return sorted(plato.id for plato in self.platos)

    @property
    def bebidas_ids(self):
        return sorted(bebida.id for bebida in self.bebidas)

    @property
    def postres_ids(self):
        return sorted(postre.id for postre in self.postres)
