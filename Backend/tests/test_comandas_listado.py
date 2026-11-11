from datetime import date, time

from src.models import Comanda
from src.models import DetalleComanda
from src.mesa.models import Mesa
from src.mozo.models import Mozo
from src.sector.models import Sector
from sqlalchemy import event


def test_listar_comandas_prioriza_las_mas_recientes(cliente, sesion):
    sector = Sector(nombre="Salón", apto_fumadores=False, piso=1)
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    sesion.add_all([sector, mesa])
    sesion.flush()

    comandas = [
        Comanda(fecha=date(2026, 6, 14), hora=time(23), mesa_id=mesa.id),
        Comanda(fecha=date(2026, 6, 15), hora=time(19), mesa_id=mesa.id),
        Comanda(fecha=date(2026, 6, 15), hora=time(21), mesa_id=mesa.id),
    ]
    sesion.add_all(comandas)
    sesion.commit()
    ids_esperados = [comandas[2].id, comandas[1].id]
    sesion.close()

    respuesta = cliente.get("/comandas?limit=2")

    assert respuesta.status_code == 200
    assert [comanda["id"] for comanda in respuesta.json()] == ids_esperados


def test_resumen_pagina_sin_consultas_por_cada_comanda(
    cliente, sesion, motor, crear_plato
):
    sector = Sector(nombre="Terraza", apto_fumadores=False, piso=1)
    mesa = Mesa(capacidad=4, disponible=False, sector=sector)
    mozo = Mozo(nombre="Ana", nro_legajo=101, estado=True)
    producto = crear_plato()
    sesion.add_all([sector, mesa, mozo, producto])
    sesion.flush()
    comandas = [
        Comanda(
            fecha=date(2026, 6, 15),
            hora=time(20, indice),
            mesa_id=mesa.id,
            mozo_id=mozo.id,
            detalles=[DetalleComanda(producto_id=producto.id, cantidad=indice + 1)],
        )
        for indice in range(3)
    ]
    sesion.add_all(comandas)
    sesion.commit()
    sesion.close()

    consultas = []

    def contar_consulta(_conexion, _cursor, sentencia, *_args):
        if sentencia.lstrip().upper().startswith("SELECT"):
            consultas.append(1)

    event.listen(motor, "before_cursor_execute", contar_consulta)
    try:
        respuesta = cliente.get("/comandas/resumen?pagina=1&tamanio_pagina=2")
    finally:
        event.remove(motor, "before_cursor_execute", contar_consulta)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["total"] == 3
    assert cuerpo["pagina"] == 1
    assert len(cuerpo["items"]) == 2
    assert cuerpo["items"][0]["mozo_nombre"] == "Ana"
    assert cuerpo["items"][0]["cantidad_items"] == 1
    assert len(consultas) == 2


def test_resumen_filtra_en_backend(cliente, sesion):
    sector = Sector(nombre="Patio", apto_fumadores=False, piso=1)
    mesa = Mesa(capacidad=2, disponible=True, sector=sector)
    mozo = Mozo(nombre="Carlos", nro_legajo=202, estado=True)
    sesion.add_all([sector, mesa, mozo])
    sesion.flush()
    sesion.add_all(
        [
            Comanda(
                fecha=date(2026, 6, 15),
                hora=time(19),
                mesa_id=mesa.id,
                mozo_id=mozo.id,
                estado="abierta",
            ),
            Comanda(
                fecha=date(2026, 6, 15),
                hora=time(18),
                mesa_id=mesa.id,
                mozo_id=mozo.id,
                estado="cerrada",
            ),
        ]
    )
    sesion.commit()
    sesion.close()

    respuesta = cliente.get("/comandas/resumen?estado=abierta&buscar=carlos")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["estado"] == "abierta"
