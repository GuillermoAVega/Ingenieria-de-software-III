# Lógica compartida por todos los subtipos. No importa FastAPI ni subpaquetes:
# recibe la clase concreta como parámetro (o la obtiene desde `registro`).
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.productos.exceptions import NombreDuplicado, ProductoNoEncontrado
from src.productos.models import Producto
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
    **campos_propios,
) -> Producto:
    """Reemplazo completo de un producto del subtipo `modelo`.

    El `dado_de_baja` de `datos` aún no se aplica: el cambio de estado se cablea
    en la tarea 4.3; mientras tanto se conserva el estado actual.
    """
    try:
        producto = obtener(sesion, modelo, producto_id)
        # El nombre solo compite con los activos si el producto queda activo
        if not producto.dado_de_baja:
            verificar_nombre_unico(sesion, datos.nombre, excluir_id=producto.id)
    except (ProductoNoEncontrado, NombreDuplicado):
        sesion.rollback()
        raise
    asignar_campos_comunes(producto, datos)
    for campo, valor in campos_propios.items():
        setattr(producto, campo, valor)
    confirmar_cambios(sesion)
    return producto
