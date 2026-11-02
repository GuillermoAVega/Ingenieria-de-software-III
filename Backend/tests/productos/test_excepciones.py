import ast
import inspect

from src.productos import exceptions as excepciones
from src.productos.exceptions import (
    BajaRestringida,
    ComponenteInactivo,
    ComponenteInvalido,
    ErrorConflicto,
    ErrorDominio,
    NombreDuplicado,
    ProductoNoEncontrado,
    SeccionInexistente,
)


def test_jerarquia_de_conflictos():
    for clase in (NombreDuplicado, ComponenteInactivo, BajaRestringida):
        assert issubclass(clase, ErrorConflicto)
    assert issubclass(ErrorConflicto, ErrorDominio)


def test_errores_de_busqueda_y_validacion_son_de_dominio_pero_no_conflictos():
    for clase in (ProductoNoEncontrado, ComponenteInvalido):
        assert issubclass(clase, ErrorDominio)
        assert not issubclass(clase, ErrorConflicto)


def test_error_dominio_es_una_excepcion_con_mensaje():
    error = ProductoNoEncontrado("Producto 7 no encontrado")
    assert isinstance(error, Exception)
    assert error.mensaje == "Producto 7 no encontrado"
    assert str(error) == "Producto 7 no encontrado"


def test_mensajes_por_defecto():
    for clase in (ProductoNoEncontrado, NombreDuplicado):
        assert clase().mensaje


def test_componente_inactivo_guarda_los_ids():
    error = ComponenteInactivo([3, 1])
    assert error.ids == [3, 1]
    assert error.mensaje


def test_componente_invalido_guarda_campo_e_ids():
    error = ComponenteInvalido("platos_ids", [9, 4])
    assert error.campo == "platos_ids"
    assert error.ids == [9, 4]
    assert error.mensaje


def test_baja_restringida_ordena_los_bloqueantes():
    error = BajaRestringida([20, 10, 15])
    assert error.bloqueantes == [10, 15, 20]
    assert error.mensaje


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


def test_las_excepciones_de_combos_no_viven_en_el_modulo_compartido():
    assert not hasattr(excepciones, "FechaHastaVencida")
    assert not hasattr(excepciones, "ComboVencidoInmutable")


def test_seccion_inexistente_es_error_de_dominio_y_guarda_el_id():
    error = SeccionInexistente(42)
    assert issubclass(SeccionInexistente, ErrorDominio)
    assert not issubclass(SeccionInexistente, ErrorConflicto)
    assert error.seccion_id == 42
    assert error.mensaje
