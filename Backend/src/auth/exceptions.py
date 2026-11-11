class ErrorUsuario(Exception):
    pass


class UsuarioDuplicado(ErrorUsuario):
    pass


class UsuarioNoEncontrado(ErrorUsuario):
    pass


class UltimoAdministrador(ErrorUsuario):
    pass
