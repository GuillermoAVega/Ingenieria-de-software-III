from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.auth.models import RolUsuario, Usuario
from src.auth.security import obtener_usuario_id
from src.database import get_db
from src.exceptions import NotAuthenticated, PermissionDenied

portador = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(portador),
    db: Session = Depends(get_db),
) -> Usuario:
    if credenciales is None or credenciales.scheme.casefold() != "bearer":
        raise NotAuthenticated
    usuario_id = obtener_usuario_id(credenciales.credentials)
    usuario = db.get(Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None or not usuario.activo:
        raise NotAuthenticated
    return usuario


def requerir_administrador(
    usuario: Usuario = Depends(obtener_usuario_actual),
) -> Usuario:
    if usuario.rol != RolUsuario.ADMINISTRADOR:
        raise PermissionDenied
    return usuario


def requerir_administrador_o_lectura(
    request: Request,
    usuario: Usuario = Depends(obtener_usuario_actual),
) -> Usuario:
    if request.method not in {"GET", "HEAD", "OPTIONS"} and (
        usuario.rol != RolUsuario.ADMINISTRADOR
    ):
        raise PermissionDenied
    return usuario
