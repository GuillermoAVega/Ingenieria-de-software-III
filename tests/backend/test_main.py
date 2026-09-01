from app.backend.main import app


def test_app_expone_las_rutas_de_clientes():
    paths = set(app.openapi()["paths"].keys())

    assert "/clientes" in paths
    assert "/clientes/{dni}" in paths
    assert "/clientes/{dni}/baja" in paths
