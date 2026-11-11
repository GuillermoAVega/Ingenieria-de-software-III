import os

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from src.auth.exceptions import (
    UltimoAdministrador,
    UsuarioDuplicado,
    UsuarioNoEncontrado,
)
from src.auth.models import RolUsuario, Usuario
from src.auth.schemas import UsuarioActualizar, UsuarioCrear
from src.auth.security import crear_hash_clave, verificar_clave


def normalizar_usuario(nombre_usuario: str) -> str:
    return nombre_usuario.strip().casefold()


def _confirmar(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        mensaje = str(error.orig).casefold()
        if "nombre_usuario" in mensaje:
            raise UsuarioDuplicado from error
        raise


def listar_usuarios(db: Session) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.nombre, Usuario.id)).all())


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        db.rollback()
        raise UsuarioNoEncontrado
    return usuario


def crear_usuario(db: Session, datos: UsuarioCrear) -> Usuario:
    nombre_usuario = normalizar_usuario(datos.nombre_usuario)
    if db.scalar(select(Usuario).where(Usuario.nombre_usuario == nombre_usuario)):
        db.rollback()
        raise UsuarioDuplicado
    usuario = Usuario(
        nombre=datos.nombre,
        nombre_usuario=nombre_usuario,
        clave_hash=crear_hash_clave(datos.clave),
        rol=datos.rol,
    )
    db.add(usuario)
    _confirmar(db)
    db.refresh(usuario)
    return usuario


def _es_ultimo_administrador(db: Session, usuario: Usuario) -> bool:
    if usuario.rol != RolUsuario.ADMINISTRADOR or not usuario.activo:
        return False
    cantidad = db.scalar(
        select(func.count(Usuario.id)).where(
            Usuario.rol == RolUsuario.ADMINISTRADOR,
            Usuario.activo.is_(True),
        )
    )
    return int(cantidad or 0) <= 1


def actualizar_usuario(
    db: Session, usuario_id: int, datos: UsuarioActualizar
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)
    cambios = datos.model_dump(exclude_unset=True)
    desactiva_admin = cambios.get("activo") is False
    cambia_rol_admin = (
        "rol" in cambios and cambios["rol"] != RolUsuario.ADMINISTRADOR
    )
    if (desactiva_admin or cambia_rol_admin) and _es_ultimo_administrador(db, usuario):
        db.rollback()
        raise UltimoAdministrador

    if "nombre_usuario" in cambios:
        nombre_usuario = normalizar_usuario(cambios.pop("nombre_usuario"))
        existente = db.scalar(
            select(Usuario).where(
                Usuario.nombre_usuario == nombre_usuario,
                Usuario.id != usuario_id,
            )
        )
        if existente:
            db.rollback()
            raise UsuarioDuplicado
        usuario.nombre_usuario = nombre_usuario
    if "clave" in cambios:
        usuario.clave_hash = crear_hash_clave(cambios.pop("clave"))
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    _confirmar(db)
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, nombre_usuario: str, clave: str) -> Usuario | None:
    usuario = db.scalar(
        select(Usuario).where(
            Usuario.nombre_usuario == normalizar_usuario(nombre_usuario),
            Usuario.activo.is_(True),
        )
    )
    if usuario is None or not verificar_clave(clave, usuario.clave_hash):
        return None
    return usuario


def crear_usuarios_iniciales(motor: Engine) -> None:
    fabrica = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    with fabrica() as db:
        if db.scalar(select(func.count(Usuario.id))):
            return
        crear_usuario(
            db,
            UsuarioCrear(
                nombre="Administrador",
                nombre_usuario=os.getenv("ADMIN_INICIAL_USUARIO", "admin"),
                clave=os.getenv("ADMIN_INICIAL_CLAVE", "admin123"),
                rol=RolUsuario.ADMINISTRADOR,
            ),
        )
        crear_usuario(
            db,
            UsuarioCrear(
                nombre="Operario",
                nombre_usuario=os.getenv("OPERARIO_INICIAL_USUARIO", "operario"),
                clave=os.getenv("OPERARIO_INICIAL_CLAVE", "operario123"),
                rol=RolUsuario.OPERARIO,
            ),
        )
