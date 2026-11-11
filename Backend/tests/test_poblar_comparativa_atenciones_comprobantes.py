from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from scripts.poblar_comparativa_atenciones_comprobantes import (
    poblar_comparativa_atenciones_comprobantes,
)
from src.models import ComprobantePago, Factura, MedioPago

ANIO = date.today().year - 1
HOY = date.today()
PERIODO = {"desde": f"{ANIO}-10-01", "hasta": f"{ANIO}-11-30"}


def _poblar(motor):
    return poblar_comparativa_atenciones_comprobantes(motor, anio=ANIO, hoy=HOY)


def test_cobra_todas_las_facturas_activas(motor):
    resumen = _poblar(motor)

    with Session(motor) as db:
        facturas = db.scalars(
            select(Factura).where(Factura.activo.is_(True))
        ).all()

        assert facturas
        assert resumen["comprobantes"]["creados"] > 0
        for factura in facturas:
            activos = [c for c in factura.comprobantes if c.activo]
            assert activos, f"La factura {factura.id} quedó sin comprobante activo."
            total = round(sum(c.importe for c in activos), 2)
            assert total == round(factura.importe_total, 2)


def test_usa_medios_de_pago_existentes(motor):
    _poblar(motor)

    with Session(motor) as db:
        medios = set(db.scalars(select(MedioPago.id)).all())
        usados = set(db.scalars(select(ComprobantePago.medio_pago_id)).all())

        assert usados
        assert usados <= medios


def test_reporte_de_medios_pago_devuelve_datos(cliente, motor):
    _poblar(motor)

    respuesta = cliente.get("/reportes/medios-pago", params=PERIODO)

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["total_comprobantes"] > 0
    assert cuerpo["total_importe"] > 0
    assert cuerpo["importe_promedio"] > 0
    assert cuerpo["medios"]
    assert round(sum(fila["importe"] for fila in cuerpo["medios"]), 2) == cuerpo[
        "total_importe"
    ]
