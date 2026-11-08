from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.productos import services
from src.productos.combos.exceptions import ComboVencidoInmutable, FechaHastaVencida
from src.productos.combos.models import ComboBebida, ComboPlato, ComboPostre
from src.productos.combos.schemas import ComboActualizar, ComboCrear, ComponenteCombo
from src.productos.exceptions import ComponenteInactivo, ComponenteInvalido, ErrorDominio
from src.productos.registro import Bebida, ComboPromocion, Plato, Postre


def _buscar_componentes(
    sesion: Session, modelo, campo: str, componentes: list[ComponenteCombo]
) -> list:
    """Devuelve los componentes del subtipo `modelo` o lanza `ComponenteInvalido(campo, faltantes)`."""
    if not componentes:
        return []
    ids = [componente.id for componente in componentes]
    encontrados = sesion.scalars(select(modelo).where(modelo.id.in_(ids))).all()
    faltantes = sorted(set(ids) - {componente.id for componente in encontrados})
    if faltantes:
        raise ComponenteInvalido(campo, faltantes)
    return list(encontrados)


def verificar_componentes_activos(*listas: list) -> None:
    """Lanza `ComponenteInactivo` con los ids (ordenados) de los componentes dados de baja."""
    inactivos = sorted(c.id for lista in listas for c in lista if c.dado_de_baja)
    if inactivos:
        raise ComponenteInactivo(inactivos)


def resolver_componentes_combo(
    sesion: Session,
    platos: list[ComponenteCombo],
    bebidas: list[ComponenteCombo],
    postres: list[ComponenteCombo],
    exigir_activos: bool,
) -> tuple[list[Plato], list[Bebida], list[Postre]]:
    """Devuelve los platos, bebidas y postres del combo tras validarlos.

    Existencia y tipo se validan siempre (`ComponenteInvalido`, 422); que estén
    activos solo si `exigir_activos` (`ComponenteInactivo`, 409).
    """
    entidades_platos = _buscar_componentes(sesion, Plato, "platos", platos)
    entidades_bebidas = _buscar_componentes(sesion, Bebida, "bebidas", bebidas)
    entidades_postres = _buscar_componentes(sesion, Postre, "postres", postres)
    if exigir_activos:
        verificar_componentes_activos(entidades_platos, entidades_bebidas, entidades_postres)
    return entidades_platos, entidades_bebidas, entidades_postres


def _sincronizar(clase, columna: str, actuales: list, nuevos: list[ComponenteCombo]) -> list:
    """Asociaciones resultantes: reutiliza las existentes (cambia `cantidad`), crea las
    nuevas y descarta las ausentes (la cascada `delete-orphan` las borra)."""
    por_id = {getattr(asociacion, columna): asociacion for asociacion in actuales}
    resultado = []
    for componente in nuevos:
        asociacion = por_id.get(componente.id)
        if asociacion is None:
            asociacion = clase(**{columna: componente.id})
        asociacion.cantidad = componente.cantidad
        resultado.append(asociacion)
    return resultado


def listar_combos(sesion: Session) -> list[ComboPromocion]:
    return services.listar(sesion, ComboPromocion)


def crear_combo(sesion: Session, datos: ComboCrear, hoy: date) -> ComboPromocion:
    """Alta de un combo activo.

    Orden: vigencia (422) → existencia de componentes (422) → sección (422) →
    componentes activos (409) → nombre (409) → commit.
    """
    try:
        if datos.fecha_hasta < hoy:
            raise FechaHastaVencida()
        platos, bebidas, postres = resolver_componentes_combo(
            sesion, datos.platos, datos.bebidas, datos.postres, exigir_activos=False
        )
        services.verificar_seccion(sesion, datos.seccion_id)
        verificar_componentes_activos(platos, bebidas, postres)
    except ErrorDominio:
        sesion.rollback()
        raise
    return services.crear_producto(
        sesion,
        ComboPromocion,
        datos,
        fecha_desde=datos.fecha_desde,
        fecha_hasta=datos.fecha_hasta,
        componentes_platos=_sincronizar(ComboPlato, "plato_id", [], datos.platos),
        componentes_bebidas=_sincronizar(ComboBebida, "bebida_id", [], datos.bebidas),
        componentes_postres=_sincronizar(ComboPostre, "postre_id", [], datos.postres),
    )


def _a_mapa(componentes: list) -> dict[int, int]:
    """`{id: cantidad}` de componentes del payload (objetos) o del combo (diccionarios)."""
    return {
        (c["id"] if isinstance(c, dict) else c.id): (
            c["cantidad"] if isinstance(c, dict) else c.cantidad
        )
        for c in componentes
    }


def _sin_otros_cambios(combo: ComboPromocion, datos: ComboActualizar) -> bool:
    """Indica si el payload (sin `dado_de_baja`) coincide con lo persistido.

    `nombre` ya viene recortado; `precio` se compara como `Decimal`;
    `descripcion`, `imagen` y `seccion_id` incluyen `None`; las listas de componentes, como `{id: cantidad}`.
    """
    return (
        datos.nombre == combo.nombre
        and Decimal(datos.precio) == combo.precio
        and datos.descripcion == combo.descripcion
        and datos.imagen == combo.imagen
        and datos.seccion_id == combo.seccion_id
        and datos.fecha_desde == combo.fecha_desde
        and datos.fecha_hasta == combo.fecha_hasta
        and _a_mapa(datos.platos) == _a_mapa(combo.platos)
        and _a_mapa(datos.bebidas) == _a_mapa(combo.bebidas)
        and _a_mapa(datos.postres) == _a_mapa(combo.postres)
    )


def _dar_de_baja_vencido(
    sesion: Session, combo: ComboPromocion, hoy: date
) -> ComboPromocion:
    """Baja de un combo vencido; si ya estaba de baja no escribe nada (idempotente)."""
    if combo.dado_de_baja:
        sesion.rollback()
        return combo
    services.dar_de_baja(sesion, ComboPromocion, combo.id, hoy)
    return combo


def actualizar_combo(
    sesion: Session, combo_id: int, datos: ComboActualizar, hoy: date
) -> ComboPromocion:
    """Reemplazo completo del combo, incluidas las listas de componentes.

    Orden: carga (404) → combo vencido (409; solo admite la baja sin otros cambios) →
    existencia y tipo de componentes (422) → sección (422) → componentes activos solo si
    el combo queda activo (409) → nombre y estado (compartidos) → commit.
    """
    try:
        combo = services.obtener(sesion, ComboPromocion, combo_id)
        if combo.fecha_hasta < hoy:
            if datos.dado_de_baja is not True or not _sin_otros_cambios(combo, datos):
                raise ComboVencidoInmutable()
            return _dar_de_baja_vencido(sesion, combo, hoy)
        queda_activo = not (
            combo.dado_de_baja if datos.dado_de_baja is None else datos.dado_de_baja
        )
        platos, bebidas, postres = resolver_componentes_combo(
            sesion,
            datos.platos,
            datos.bebidas,
            datos.postres,
            exigir_activos=False,
        )
        services.verificar_seccion(sesion, datos.seccion_id)
        if queda_activo:
            verificar_componentes_activos(platos, bebidas, postres)
    except ErrorDominio:
        sesion.rollback()
        raise

    def verificar_reactivacion(combo: ComboPromocion) -> None:
        if combo.fecha_hasta < hoy:
            raise ComboVencidoInmutable()
        verificar_componentes_activos(platos, bebidas, postres)

    return services.actualizar_producto(
        sesion,
        ComboPromocion,
        combo_id,
        datos,
        hoy,
        verificar_reactivacion=verificar_reactivacion,
        fecha_desde=datos.fecha_desde,
        fecha_hasta=datos.fecha_hasta,
        componentes_platos=_sincronizar(
            ComboPlato, "plato_id", combo.componentes_platos, datos.platos
        ),
        componentes_bebidas=_sincronizar(
            ComboBebida, "bebida_id", combo.componentes_bebidas, datos.bebidas
        ),
        componentes_postres=_sincronizar(
            ComboPostre, "postre_id", combo.componentes_postres, datos.postres
        ),
    )
