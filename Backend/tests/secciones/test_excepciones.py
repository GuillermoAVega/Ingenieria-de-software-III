import ast
import inspect

from src.productos import exceptions as excepciones_productos
from src.productos.exceptions import ErrorDominio
from src.secciones import exceptions as excepciones
from src.secciones.exceptions import (
    ErrorSeccion,
    NombreSeccionDuplicado,
    SeccionNoEncontrada,
)


def test_jerarquia_de_errores_de_seccion():
    for clase in (SeccionNoEncontrada, NombreSeccionDuplicado):
        assert issubclass(clase, ErrorSeccion)
    assert issubclass(ErrorSeccion, Exception)


def test_jerarquia_disjunta_de_los_errores_de_productos():
    for clase in (ErrorSeccion, SeccionNoEncontrada, NombreSeccionDuplicado):
        assert not issubclass(clase, ErrorDominio)
    assert not issubclass(ErrorDominio, ErrorSeccion)
    assert excepciones_productos.ErrorDominio is ErrorDominio


def test_error_de_seccion_guarda_el_mensaje():
    error = SeccionNoEncontrada("Sección 7 no encontrada")
    assert error.mensaje == "Sección 7 no encontrada"
    assert str(error) == "Sección 7 no encontrada"


def test_mensajes_por_defecto():
    for clase in (SeccionNoEncontrada, NombreSeccionDuplicado):
        assert clase().mensaje


def test_excepciones_no_importan_fastapi_ni_productos():
    arbol = ast.parse(inspect.getsource(excepciones))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            modulos.add(nodo.module or "")
    assert not any(m.split(".")[0] == "fastapi" for m in modulos)
    assert not any(m.startswith("src.productos") for m in modulos)
