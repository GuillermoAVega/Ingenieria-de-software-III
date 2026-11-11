from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.auth import services
from src.auth.dependencies import obtener_usuario_actual, requerir_administrador
from src.auth.exceptions import (
    UltimoAdministrador,
    UsuarioDuplicado,
    UsuarioNoEncontrado,
)
from src.auth.models import Usuario
from src.auth.schemas import (
    CredencialesLogin,
    SesionRespuesta,
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioRespuesta,
)
from src.auth.security import crear_token
from src.database import get_db
from src.exceptions import NotAuthenticated

router = APIRouter(tags=["Autenticación"])


@router.post("/auth/login", response_model=SesionRespuesta)
def iniciar_sesion(datos: CredencialesLogin, db: Session = Depends(get_db)):
    usuario = services.autenticar(db, datos.nombre_usuario, datos.clave)
    if usuario is None:
        raise NotAuthenticated
    return SesionRespuesta(token=crear_token(usuario.id), usuario=usuario)


@router.get("/auth/me", response_model=UsuarioRespuesta)
def usuario_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario


@router.get(
    "/usuarios",
    response_model=list[UsuarioRespuesta],
    dependencies=[Depends(requerir_administrador)],
)
def listar_usuarios(db: Session = Depends(get_db)):
    return services.listar_usuarios(db)


@router.post(
    "/usuarios",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_administrador)],
)
def crear_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    return services.crear_usuario(db, datos)


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRespuesta,
    dependencies=[Depends(requerir_administrador)],
)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return services.obtener_usuario(db, usuario_id)


@router.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioRespuesta,
    dependencies=[Depends(requerir_administrador)],
)
def actualizar_usuario(
    usuario_id: int, datos: UsuarioActualizar, db: Session = Depends(get_db)
):
    return services.actualizar_usuario(db, usuario_id, datos)


def _manejador(mensaje: str, codigo: int):
    async def manejar(_request, _error):
        return JSONResponse(status_code=codigo, content={"detail": mensaje})

    return manejar


MANEJADORES_EXCEPCIONES = {
    UsuarioDuplicado: _manejador("El nombre de usuario ya existe.", 409),
    UsuarioNoEncontrado: _manejador("El usuario no existe.", 404),
    UltimoAdministrador: _manejador(
        "No se puede desactivar ni cambiar el rol del último administrador.", 409
    ),
}
