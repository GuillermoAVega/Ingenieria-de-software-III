import ast
import importlib
import inspect

from src.productos import exceptions as excepciones_productos
from src.productos.exceptions import ErrorDominio
from src.secciones import exceptions as excepciones
from src.secciones.exceptions import (
    ErrorSeccion,
    NombreSeccionDuplicado,
    PosicionSeccionDuplicada,
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


def test_pos_11_posicion_duplicada_es_un_error_de_seccion_disjunto():
    assert issubclass(PosicionSeccionDuplicada, ErrorSeccion)
    assert not issubclass(PosicionSeccionDuplicada, ErrorDominio)
    assert not issubclass(PosicionSeccionDuplicada, NombreSeccionDuplicado)
    assert not issubclass(NombreSeccionDuplicado, PosicionSeccionDuplicada)


def test_pos_11_posicion_duplicada_tiene_el_mensaje_estandar():
    assert PosicionSeccionDuplicada.MENSAJE == "Ya existe una sección en esa posición"
    assert PosicionSeccionDuplicada().mensaje == PosicionSeccionDuplicada.MENSAJE
    assert str(PosicionSeccionDuplicada()) == "Ya existe una sección en esa posición"


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


def _importaciones(modulo):
    arbol = ast.parse(inspect.getsource(modulo))
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            base = nodo.module or ""
            importados.add(base)
            # `from src import productos` importa el paquete como nombre
            importados.update(f"{base}.{alias.name}" for alias in nodo.names)
    return importados


def test_productos_ids_secciones_no_importa_productos():
    for nombre in ("models", "schemas", "services", "router"):
        modulo = importlib.import_module(f"src.secciones.{nombre}")
        importados = _importaciones(modulo)
        ofensores = {
            m for m in importados if m == "src.productos" or m.startswith("src.productos.")
        }
        assert not ofensores, f"src.secciones.{nombre} importa {ofensores}"
