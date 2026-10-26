from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    false,
    text,
)
from sqlalchemy.orm import mapped_column, relationship

from src.models import ModeloBase
from src.productos.constants import (
    CANT_PERSONAS_MIN,
    DESCRIPCION_MAX,
    NOMBRE_MAX,
    PRECIO_DECIMALES,
    PRECIO_DIGITOS,
    TIPO_BEBIDA,
    TIPO_COMBO_PROMOCION,
    TIPO_MAX,
    TIPO_MENU_EJECUTIVO,
    TIPO_PLATO,
    TIPO_POSTRE,
)

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

    def __new__(cls, *args, **kw):
        # Se valida en __new__ porque la instrumentación de SQLAlchemy envuelve
        # __init__ y lanzaría InvalidRequestError antes de llegar a nuestro código
        if cls is Producto:
            raise TypeError("Producto es abstracto")
        return super().__new__(cls)


class Plato(Producto):
    __tablename__ = "plato"
    __table_args__ = (
        CheckConstraint(
            f"cant_personas >= {CANT_PERSONAS_MIN}", name="ck_plato_cant_personas_minima"
        ),
    )
    __mapper_args__ = {"polymorphic_identity": TIPO_PLATO}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cant_personas = mapped_column(Integer, nullable=False)

    menus = relationship(
        "MenuEjecutivo", foreign_keys="MenuEjecutivo.plato_id", back_populates="plato"
    )
    combos = relationship("ComboPromocion", secondary=combo_plato, back_populates="platos")


class Bebida(Producto):
    __tablename__ = "bebida"
    __mapper_args__ = {"polymorphic_identity": TIPO_BEBIDA}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    es_alcoholica = mapped_column(Boolean, nullable=False)

    combos = relationship("ComboPromocion", secondary=combo_bebida, back_populates="bebidas")


class Postre(Producto):
    __tablename__ = "postre"
    __mapper_args__ = {"polymorphic_identity": TIPO_POSTRE}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)

    menus = relationship(
        "MenuEjecutivo", foreign_keys="MenuEjecutivo.postre_id", back_populates="postre"
    )
    combos = relationship("ComboPromocion", secondary=combo_postre, back_populates="postres")


class MenuEjecutivo(Producto):
    __tablename__ = "menu_ejecutivo"
    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    plato_id = mapped_column(ForeignKey("plato.id"), nullable=False)
    postre_id = mapped_column(ForeignKey("postre.id"), nullable=False)

    # Hay varias FK hacia la jerarquía: se explicita cuál une con `producto`
    __mapper_args__ = {
        "polymorphic_identity": TIPO_MENU_EJECUTIVO,
        "inherit_condition": id == Producto.id,
    }

    plato = relationship("Plato", foreign_keys=[plato_id], back_populates="menus")
    postre = relationship("Postre", foreign_keys=[postre_id], back_populates="menus")


class ComboPromocion(Producto):
    __tablename__ = "combo_promocion"
    __table_args__ = (
        CheckConstraint("fecha_desde <= fecha_hasta", name="ck_combo_rango_de_fechas"),
    )
    __mapper_args__ = {"polymorphic_identity": TIPO_COMBO_PROMOCION}

    id = mapped_column(ForeignKey("producto.id"), primary_key=True)
    fecha_desde = mapped_column(Date, nullable=False)
    fecha_hasta = mapped_column(Date, nullable=False)

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
