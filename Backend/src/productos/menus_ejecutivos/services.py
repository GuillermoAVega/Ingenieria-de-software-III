from datetime import date

from sqlalchemy.orm import Session

from src.productos import services
from src.productos.exceptions import (
    ComponenteInactivo,
    ComponenteInvalido,
    ErrorDominio,
)
from src.productos.menus_ejecutivos.schemas import MenuActualizar, MenuCrear
from src.productos.registro import MenuEjecutivo, Plato, Postre


def resolver_componentes_menu(
    sesion: Session, plato_id: int, postre_id: int, exigir_activos: bool
) -> tuple[Plato, Postre]:
    """Devuelve el Plato y el Postre del menú tras validarlos.

    Existencia y tipo se validan siempre (`ComponenteInvalido`, 422); que estén
    activos solo si `exigir_activos` (`ComponenteInactivo`, 409).
    """
    plato = sesion.get(Plato, plato_id)
    if plato is None:
        raise ComponenteInvalido("plato_id", [plato_id])
    postre = sesion.get(Postre, postre_id)
    if postre is None:
        raise ComponenteInvalido("postre_id", [postre_id])
    if exigir_activos:
        verificar_componentes_activos(plato, postre)
    return plato, postre


def verificar_componentes_activos(plato: Plato, postre: Postre) -> None:
    """Lanza `ComponenteInactivo` con los ids (ordenados) de los componentes dados de baja."""
    inactivos = sorted(c.id for c in (plato, postre) if c.dado_de_baja)
    if inactivos:
        raise ComponenteInactivo(inactivos)


def crear_menu(sesion: Session, datos: MenuCrear) -> MenuEjecutivo:
    """Alta de un menú activo.

    Orden: existencia de componentes (422) → sección (422) → componentes activos (409) →
    nombre (409) → commit.
    """
    try:
        plato, postre = resolver_componentes_menu(
            sesion, datos.plato_id, datos.postre_id, exigir_activos=False
        )
        services.verificar_seccion(sesion, datos.seccion_id)
        verificar_componentes_activos(plato, postre)
    except ErrorDominio:
        sesion.rollback()
        raise
    return services.crear_producto(
        sesion, MenuEjecutivo, datos, plato_id=datos.plato_id, postre_id=datos.postre_id
    )


def actualizar_menu(
    sesion: Session, menu_id: int, datos: MenuActualizar, hoy: date
) -> MenuEjecutivo:
    """Reemplazo completo del menú.

    Orden: carga (404) → existencia y tipo de componentes (422) → sección (422) →
    componentes activos solo si el menú queda activo (409) → nombre y estado
    (compartidos) → commit.
    """
    try:
        menu = services.obtener(sesion, MenuEjecutivo, menu_id)
        queda_activo = not (
            menu.dado_de_baja if datos.dado_de_baja is None else datos.dado_de_baja
        )
        plato, postre = resolver_componentes_menu(
            sesion, datos.plato_id, datos.postre_id, exigir_activos=False
        )
        services.verificar_seccion(sesion, datos.seccion_id)
        if queda_activo:
            verificar_componentes_activos(plato, postre)
    except ErrorDominio:
        sesion.rollback()
        raise
    return services.actualizar_producto(
        sesion,
        MenuEjecutivo,
        menu_id,
        datos,
        hoy,
        verificar_reactivacion=lambda _menu: verificar_componentes_activos(plato, postre),
        plato_id=datos.plato_id,
        postre_id=datos.postre_id,
    )
