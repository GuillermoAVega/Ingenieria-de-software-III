import itertools
from datetime import date, datetime, time

import pytest

from src.mesa.models import Mesa
from src.models import Comanda, ComprobantePago, Factura, MedioPago
from src.mozo.models import Mozo
from src.sector.models import Sector

URL = "/reportes/medios-pago"
PERIODO = {"desde": "2026-06-01", "hasta": "2026-06-30"}

_secuencia = itertools.count(1)


@pytest.fixture
def medios(persistir):
    efectivo, debito, credito = persistir(
        MedioPago(descripcion="Efectivo"),
        MedioPago(descripcion="Tarjeta de débito"),
        MedioPago(descripcion="Tarjeta de crédito"),
    )
    return {"efectivo": efectivo, "debito": debito, "credito": credito}


@pytest.fixture
def crear_pagos(sesion, persistir):
    """Crea una factura con los comprobantes indicados y devuelve su id.

    `pagos` es una lista de `(medio_pago_id, importe, activo)`.
    """

    def _crear(
        emision: datetime,
        pagos: list[tuple[int, float, bool]],
        *,
        factura_activa: bool = True,
        factura_emision: datetime | None = None,
    ) -> int:
        numero = next(_secuencia)
        sector = Sector(
            nombre=f"Salón reporte {numero}",
            apto_fumadores=False,
            piso="Planta baja",
        )
        mesa = Mesa(capacidad=2, disponible=True, sector=sector)
        mozo = Mozo(nombre="Luis", nro_legajo=9000 + numero)
        mesa_id, mozo_id = persistir(mesa, mozo)

        comanda = Comanda(
            fecha=(factura_emision or emision).date(),
            hora=time(12),
            mozo_id=mozo_id,
            mesa_id=mesa_id,
        )
        comanda_id = persistir(comanda)
        factura = Factura(
            importe_total=sum(importe for _, importe, _ in pagos),
            fecha_hora_emision=factura_emision or emision,
            activo=factura_activa,
            comanda_id=comanda_id,
        )
        sesion.add(factura)
        sesion.flush()
        factura_id = factura.id
        for medio_id, importe, activo in pagos:
            sesion.add(
                ComprobantePago(
                    importe=importe,
                    fecha_hora_emision=emision,
                    activo=activo,
                    factura_id=factura_id,
                    medio_pago_id=medio_id,
                )
            )
        sesion.commit()
        sesion.close()
        return factura_id

    return _crear


def _reporte(cliente, **params):
    respuesta = cliente.get(URL, params={**PERIODO, **params})
    assert respuesta.status_code == 200
    return respuesta.json()


def test_estructura_totales_y_porcentajes(cliente, medios, crear_pagos):
    crear_pagos(
        datetime(2026, 6, 5, 12),
        [
            (medios["efectivo"], 100, True),
            (medios["efectivo"], 50, True),
            (medios["debito"], 30, True),
        ],
    )

    cuerpo = _reporte(cliente)

    assert cuerpo["desde"] == "2026-06-01"
    assert cuerpo["hasta"] == "2026-06-30"
    assert cuerpo["total_comprobantes"] == 3
    assert cuerpo["total_importe"] == 180.0
    assert cuerpo["importe_promedio"] == 60.0
    assert cuerpo["medios"] == [
        {
            "medio_pago_id": medios["efectivo"],
            "descripcion": "Efectivo",
            "cantidad_comprobantes": 2,
            "importe": 150.0,
            "importe_promedio": 75.0,
            "porcentaje_uso": 66.67,
            "porcentaje_importe": 83.33,
        },
        {
            "medio_pago_id": medios["debito"],
            "descripcion": "Tarjeta de débito",
            "cantidad_comprobantes": 1,
            "importe": 30.0,
            "importe_promedio": 30.0,
            "porcentaje_uso": 33.33,
            "porcentaje_importe": 16.67,
        },
    ]


def test_pago_dividido_entre_dos_medios(cliente, medios, crear_pagos):
    crear_pagos(
        datetime(2026, 6, 10, 20),
        [(medios["efectivo"], 50, True), (medios["debito"], 50, True)],
    )

    cuerpo = _reporte(cliente)

    assert cuerpo["total_comprobantes"] == 2
    assert cuerpo["total_importe"] == 100.0
    assert cuerpo["importe_promedio"] == 50.0
    assert {
        fila["descripcion"]: (
            fila["cantidad_comprobantes"],
            fila["importe"],
            fila["porcentaje_uso"],
            fila["porcentaje_importe"],
        )
        for fila in cuerpo["medios"]
    } == {
        "Efectivo": (1, 50.0, 50.0, 50.0),
        "Tarjeta de débito": (1, 50.0, 50.0, 50.0),
    }


def test_excluye_comprobantes_y_facturas_inactivas(cliente, medios, crear_pagos):
    crear_pagos(datetime(2026, 6, 5, 12), [(medios["efectivo"], 100, True)])
    crear_pagos(datetime(2026, 6, 6, 12), [(medios["efectivo"], 100, False)])
    crear_pagos(
        datetime(2026, 6, 7, 12),
        [(medios["debito"], 100, True)],
        factura_activa=False,
    )

    cuerpo = _reporte(cliente)

    assert cuerpo["total_comprobantes"] == 1
    assert cuerpo["total_importe"] == 100.0
    assert [fila["descripcion"] for fila in cuerpo["medios"]] == ["Efectivo"]


def test_periodo_inclusivo_en_ambos_bordes(cliente, medios, crear_pagos):
    crear_pagos(datetime(2026, 5, 31, 23, 59, 59), [(medios["efectivo"], 100, True)])
    crear_pagos(datetime(2026, 6, 1, 0, 0, 0), [(medios["efectivo"], 100, True)])
    crear_pagos(datetime(2026, 6, 30, 23, 59, 59), [(medios["debito"], 100, True)])
    crear_pagos(datetime(2026, 7, 1, 0, 0, 0), [(medios["credito"], 100, True)])

    cuerpo = _reporte(cliente)

    assert cuerpo["total_comprobantes"] == 2
    assert {
        fila["descripcion"]: fila["cantidad_comprobantes"] for fila in cuerpo["medios"]
    } == {"Efectivo": 1, "Tarjeta de débito": 1}


def test_usa_fecha_del_pago_no_de_la_factura(cliente, medios, crear_pagos):
    crear_pagos(
        datetime(2026, 6, 15, 12),
        [(medios["efectivo"], 100, True)],
        factura_emision=datetime(2026, 5, 1, 12),
    )
    crear_pagos(
        datetime(2026, 7, 15, 12),
        [(medios["debito"], 100, True)],
        factura_emision=datetime(2026, 6, 15, 12),
    )

    cuerpo = _reporte(cliente)

    assert [fila["descripcion"] for fila in cuerpo["medios"]] == ["Efectivo"]


def test_periodo_sin_pagos(cliente):
    cuerpo = _reporte(cliente)

    assert cuerpo == {
        "desde": "2026-06-01",
        "hasta": "2026-06-30",
        "total_comprobantes": 0,
        "total_importe": 0.0,
        "importe_promedio": 0.0,
        "medios": [],
    }


def test_ordena_por_cantidad_importe_y_descripcion(cliente, medios, crear_pagos):
    crear_pagos(
        datetime(2026, 6, 5, 12),
        [
            (medios["efectivo"], 100, True),
            (medios["efectivo"], 50, True),
        ],
    )
    crear_pagos(datetime(2026, 6, 6, 12), [(medios["debito"], 200, True)])
    crear_pagos(datetime(2026, 6, 7, 12), [(medios["credito"], 200, True)])

    cuerpo = _reporte(cliente)

    assert [fila["descripcion"] for fila in cuerpo["medios"]] == [
        "Efectivo",
        "Tarjeta de crédito",
        "Tarjeta de débito",
    ]


def test_incluye_medio_inactivo_con_uso_historico(cliente, persistir, crear_pagos):
    cheque = persistir(MedioPago(descripcion="Cheque", activo=False))
    crear_pagos(datetime(2026, 6, 5, 12), [(cheque, 100, True)])

    cuerpo = _reporte(cliente)

    assert [fila["descripcion"] for fila in cuerpo["medios"]] == ["Cheque"]
    assert cuerpo["medios"][0]["porcentaje_uso"] == 100.0


def test_validaciones(cliente):
    assert cliente.get(URL).status_code == 422
    assert cliente.get(URL, params={"desde": "2026-06-01"}).status_code == 422
    assert cliente.get(URL, params={"hasta": "2026-06-30"}).status_code == 422
    assert (
        cliente.get(
            URL, params={"desde": "2026-06-30", "hasta": "2026-06-01"}
        ).status_code
        == 422
    )
    assert (
        cliente.get(
            URL, params={"desde": "no-es-fecha", "hasta": "2026-06-30"}
        ).status_code
        == 422
    )
