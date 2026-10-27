# Único módulo que conoce todos los subpaquetes: al importarlo quedan cargados
# los cinco modelos y los mappers pueden resolver las relaciones por cadena
from src.productos.bebidas.models import Bebida
from src.productos.combos.models import (
    ComboPromocion,
    combo_bebida,
    combo_plato,
    combo_postre,
)
from src.productos.constants import (
    TIPO_BEBIDA,
    TIPO_COMBO_PROMOCION,
    TIPO_MENU_EJECUTIVO,
    TIPO_PLATO,
    TIPO_POSTRE,
)
from src.productos.menus_ejecutivos.models import MenuEjecutivo
from src.productos.platos.models import Plato
from src.productos.postres.models import Postre

# Clase concreta de cada valor del discriminador `tipo`
MODELOS_POR_TIPO = {
    TIPO_PLATO: Plato,
    TIPO_BEBIDA: Bebida,
    TIPO_POSTRE: Postre,
    TIPO_MENU_EJECUTIVO: MenuEjecutivo,
    TIPO_COMBO_PROMOCION: ComboPromocion,
}

# Restricción de baja por tipo: (columna de `menu_ejecutivo` o None, tabla de
# asociación del combo, columna del componente en esa tabla). Los compuestos
# no figuran: no tienen RESTRICT.
RESTRICT_POR_TIPO = {
    TIPO_PLATO: ("plato_id", combo_plato, "plato_id"),
    TIPO_POSTRE: ("postre_id", combo_postre, "postre_id"),
    TIPO_BEBIDA: (None, combo_bebida, "bebida_id"),
}

__all__ = [
    "MODELOS_POR_TIPO",
    "RESTRICT_POR_TIPO",
    "Bebida",
    "ComboPromocion",
    "MenuEjecutivo",
    "Plato",
    "Postre",
    "combo_bebida",
    "combo_plato",
    "combo_postre",
]
