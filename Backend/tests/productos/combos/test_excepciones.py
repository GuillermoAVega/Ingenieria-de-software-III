import ast
import inspect

from src.productos.combos import exceptions as excepciones
from src.productos.combos.exceptions import ComboVencidoInmutable, FechaHastaVencida
from src.productos.exceptions import ErrorConflicto, ErrorDominio


def test_combo_vencido_inmutable_es_un_conflicto():
    assert issubclass(ComboVencidoInmutable, ErrorConflicto)
    assert ComboVencidoInmutable().mensaje


def test_fecha_hasta_vencida_es_un_error_de_dominio_pero_no_un_conflicto():
    assert issubclass(FechaHastaVencida, ErrorDominio)
    assert not issubclass(FechaHastaVencida, ErrorConflicto)
    assert FechaHastaVencida().mensaje


def test_el_modulo_no_importa_fastapi():
    arbol = ast.parse(inspect.getsource(excepciones))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name.split(".")[0] for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module.split(".")[0])
    assert "fastapi" not in modulos
    assert "starlette" not in modulos
