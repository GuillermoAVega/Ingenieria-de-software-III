# Lógica compartida por todos los subtipos. No importa FastAPI ni subpaquetes:
# recibe la clase concreta como parámetro (o la obtiene desde `registro`).
from collections.abc import Callable
from datetime import date

from sqlalchemy import select, union
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.productos.exceptions import (
    BajaRestringida,
    ErrorDominio,
    NombreDuplicado,
    ProductoNoEncontrado,
)
from src.productos.models import Producto
from src.productos.registro import RESTRICT_POR_TIPO, ComboPromocion, MenuEjecutivo
from src.productos.schemas import ProductoBase


def obtener_hoy() -> date:
    """Fecha actual; los routers la inyectan para poder sobrescribirla en las pruebas."""
    return date.today()


def normalizar_nombre(nombre: str) -> str:
    """Clave de unicidad: sin espacios sobrantes y sin distinguir mayúsculas (sí tildes)."""
    return nombre.strip().casefold()


def obtener(sesion: Session, modelo: type[Producto], producto_id: int) -> Producto:
    """Devuelve el producto del subtipo `modelo` (activo o dado de baja) o lanza 404."""
    producto = sesion.get(modelo, producto_id)
    if producto is None:
        raise ProductoNoEncontrado()
    return producto


def verificar_nombre_unico(
    sesion: Session, nombre: str, excluir_id: int | None = None
) -> None:
    """Lanza `NombreDuplicado` si otro producto ACTIVO (de cualquier subtipo) usa el nombre."""
    consulta = select(Producto.id).where(
        Producto.nombre_normalizado == normalizar_nombre(nombre),
        Producto.dado_de_baja.is_(False),
    )
    if excluir_id is not None:
        consulta = consulta.where(Producto.id != excluir_id)
    if sesion.execute(consulta.limit(1)).first() is not None:
        raise NombreDuplicado()


def buscar_bloqueantes(sesion: Session, producto: Producto, hoy: date) -> list[int]:
    """Ids ordenados de los compuestos activos que impiden dar de baja al producto.

    Bloquean los menús activos que lo usan y los combos activos que lo usan y
    cuya `fecha_hasta` no es anterior a `hoy` (incluye los que aún no empezaron).
    """
    restriccion = RESTRICT_POR_TIPO.get(producto.tipo)
    if restriccion is None:
        return []
    columna_menu, tabla_combo, columna_combo = restriccion

    ramas = []
    if columna_menu is not None:
        ramas.append(
            select(MenuEjecutivo.id.label("id")).where(
                getattr(MenuEjecutivo, columna_menu) == producto.id,
                MenuEjecutivo.dado_de_baja.is_(False),
            )
        )
    ramas.append(
        select(ComboPromocion.id.label("id"))
        .join(tabla_combo, tabla_combo.c.combo_id == ComboPromocion.id)
        .where(
            tabla_combo.c[columna_combo] == producto.id,
            ComboPromocion.dado_de_baja.is_(False),
            ComboPromocion.fecha_hasta >= hoy,
        )
    )
    consulta = union(*ramas).order_by("id")
    return list(sesion.scalars(consulta))


def aplicar_cambio_estado(
    sesion: Session,
    producto: Producto,
    nuevo_estado: bool | None,
    hoy: date,
    verificar_reactivacion: Callable[[Producto], None] | None = None,
    nombre: str | None = None,
) -> None:
    """Aplica `dado_de_baja` al producto sin confirmar (lo hace quien llama).

    `None` o el estado actual no hacen nada (idempotente). Una baja de Plato,
    Bebida o Postre se rechaza con `BajaRestringida` si otros compuestos activos
    dependen de él; los compuestos no tienen restricción. Una reactivación ejecuta
    primero `verificar_reactivacion` (gancho del subtipo compuesto) y luego la
    unicidad de `nombre` (por defecto, el nombre actual del producto).
    """
    if nuevo_estado is None or nuevo_estado == producto.dado_de_baja:
        return
    if nuevo_estado:
        bloqueantes = buscar_bloqueantes(sesion, producto, hoy)
        if bloqueantes:
            raise BajaRestringida(bloqueantes)
    else:
        if verificar_reactivacion is not None:
            verificar_reactivacion(producto)
        verificar_nombre_unico(
            sesion, nombre if nombre is not None else producto.nombre, excluir_id=producto.id
        )
    producto.dado_de_baja = nuevo_estado


def dar_de_baja(sesion: Session, modelo: type[Producto], producto_id: int, hoy: date) -> None:
    """Baja lógica del producto del subtipo `modelo` (DELETE); repetirla no tiene efecto."""
    try:
        producto = obtener(sesion, modelo, producto_id)
        aplicar_cambio_estado(sesion, producto, True, hoy)
    except (ProductoNoEncontrado, BajaRestringida):
        sesion.rollback()
        raise
    confirmar_cambios(sesion)


def asignar_campos_comunes(producto: Producto, datos: ProductoBase) -> None:
    """Copia los campos comunes (reemplazo completo) y recalcula la clave de unicidad."""
    producto.nombre = datos.nombre
    producto.nombre_normalizado = normalizar_nombre(datos.nombre)
    producto.precio = datos.precio
    producto.descripcion = datos.descripcion
    producto.imagen = datos.imagen


def confirmar_cambios(sesion: Session) -> None:
    """Confirma la transacción; el índice parcial de nombre activo se traduce a 409."""
    try:
        sesion.commit()
    except IntegrityError as error:
        sesion.rollback()
        if "nombre_normalizado" in str(error.orig):
            raise NombreDuplicado() from error
        raise


def crear_producto(
    sesion: Session, modelo: type[Producto], datos: ProductoBase, **campos_propios
) -> Producto:
    """Alta de un producto activo del subtipo `modelo` con sus campos propios."""
    try:
        verificar_nombre_unico(sesion, datos.nombre)
    except NombreDuplicado:
        sesion.rollback()
        raise
    producto = modelo(**campos_propios)
    asignar_campos_comunes(producto, datos)
    sesion.add(producto)
    confirmar_cambios(sesion)
    return producto


def actualizar_producto(
    sesion: Session,
    modelo: type[Producto],
    producto_id: int,
    datos: ProductoBase,
    hoy: date,
    verificar_reactivacion: Callable[[Producto], None] | None = None,
    **campos_propios,
) -> Producto:
    """Reemplazo completo de un producto del subtipo `modelo`.

    `datos.dado_de_baja` (si el esquema lo trae) omitido conserva el estado actual.
    Orden: carga (404) → unicidad del nombre si el producto queda activo (409) →
    cambio de estado (409 si la baja está restringida) → asignación → commit.
    `verificar_reactivacion` es el gancho del subtipo compuesto para las reactivaciones.
    """
    nuevo_estado = getattr(datos, "dado_de_baja", None)
    try:
        producto = obtener(sesion, modelo, producto_id)
        estado_resultante = producto.dado_de_baja if nuevo_estado is None else nuevo_estado
        # Una reactivación comprueba el nombre dentro de `aplicar_cambio_estado`
        if not estado_resultante and not producto.dado_de_baja:
            verificar_nombre_unico(sesion, datos.nombre, excluir_id=producto.id)
        aplicar_cambio_estado(
            sesion,
            producto,
            nuevo_estado,
            hoy,
            verificar_reactivacion=verificar_reactivacion,
            nombre=datos.nombre,
        )
    except ErrorDominio:
        # Incluye los errores del gancho de reactivación del subtipo compuesto
        sesion.rollback()
        raise
    asignar_campos_comunes(producto, datos)
    for campo, valor in campos_propios.items():
        setattr(producto, campo, valor)
    confirmar_cambios(sesion)
    return producto
