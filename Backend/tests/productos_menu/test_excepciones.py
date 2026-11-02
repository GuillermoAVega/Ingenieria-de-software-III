import ast
import inspect

from src.productos.exceptions import ErrorDominio
from src.productos_menu import exceptions as excepciones
from src.productos_menu.exceptions import (
    ErrorProductoMenu,
    FechaMenuOcupada,
    ProductoDadoDeBaja,
    ProductoInexistente,
    ProductoMenuNoEncontrado,
)
from src.secciones.exceptions import ErrorSeccion

CONCRETAS = (
    ProductoInexistente,
    ProductoDadoDeBaja,
    FechaMenuOcupada,
    ProductoMenuNoEncontrado,
)


def test_excepciones_heredan_de_error_producto_menu():
    for clase in CONCRETAS:
        assert issubclass(clase, ErrorProductoMenu)
    assert issubclass(ErrorProductoMenu, Exception)


def test_jerarquia_disjunta_de_productos_y_secciones():
    for clase in (ErrorProductoMenu, *CONCRETAS):
        assert not issubclass(clase, ErrorDominio)
        assert not issubclass(clase, ErrorSeccion)
    assert not issubclass(ErrorDominio, ErrorProductoMenu)
    assert not issubclass(ErrorSeccion, ErrorProductoMenu)


def test_producto_inexistente_guarda_producto_id():
    error = ProductoInexistente(42)

    assert error.producto_id == 42
    assert error.mensaje


def test_cada_excepcion_tiene_mensaje():
    instancias = (
        ErrorProductoMenu(),
        ProductoInexistente(1),
        ProductoDadoDeBaja(),
        FechaMenuOcupada(),
        ProductoMenuNoEncontrado(),
    )
    for instancia in instancias:
        assert instancia.mensaje
        assert str(instancia) == instancia.mensaje


def test_mensajes_de_baja_y_fecha_ocupada_difieren():
    assert ProductoDadoDeBaja().mensaje != FechaMenuOcupada().mensaje


def test_mensaje_personalizado():
    assert FechaMenuOcupada("otro").mensaje == "otro"


def test_excepciones_no_importan_fastapi():
    arbol = ast.parse(inspect.getsource(excepciones))
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            importados.add(nodo.module)
    assert not any(m.split(".")[0] == "fastapi" for m in importados)
