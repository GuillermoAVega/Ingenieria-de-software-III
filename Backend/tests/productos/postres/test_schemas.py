from src.productos.postres.schemas import PostreActualizar, PostreCrear, PostreRespuesta


def test_postre_acepta_solo_los_campos_comunes():
    postre = PostreCrear(nombre="Flan", precio="600.00")
    assert postre.nombre == "Flan"
    assert postre.descripcion is None


def test_actualizar_agrega_dado_de_baja_opcional():
    assert PostreActualizar(nombre="Flan", precio="600.00").dado_de_baja is None
    assert (
        PostreActualizar(nombre="Flan", precio="600.00", dado_de_baja=True).dado_de_baja
        is True
    )


def test_respuesta_se_construye_desde_el_modelo(crear_postre):
    postre = crear_postre()
    postre.id = 9
    postre.dado_de_baja = True
    respuesta = PostreRespuesta.model_validate(postre)
    assert respuesta.tipo == "postre"
    assert respuesta.dado_de_baja is True
