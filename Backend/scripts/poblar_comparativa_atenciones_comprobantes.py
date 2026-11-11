"""Genera datos comparativos con atenciones y comprobantes de pago completos.

Uso (desde ``Backend/``)::

    venv/bin/python -m scripts.poblar_comparativa_atenciones_comprobantes
    venv/bin/python -m scripts.poblar_comparativa_atenciones_comprobantes --anio 2025

La población recrea todas las tablas, por lo que no debe ejecutarse sobre una
base cuyos datos se quieran conservar.
"""

import argparse
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from scripts.poblar_comparativa_atenciones import (  # noqa: E402
    poblar_comparativa_atenciones,
)
from src.models import ComprobantePago, Factura, MedioPago  # noqa: E402

CENTAVOS = Decimal("0.01")


def poblar_comparativa_atenciones_comprobantes(
    motor: Engine, anio: int | None = None, hoy: date | None = None
) -> dict:
    """Recrea la base y garantiza un cobro activo para cada factura activa."""
    hoy = hoy or date.today()
    anio = anio or hoy.year
    resumen = poblar_comparativa_atenciones(motor, anio=anio, hoy=hoy)
    creados = 0

    fabrica = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    with fabrica() as db:
        medios = db.scalars(
            select(MedioPago).where(MedioPago.activo.is_(True)).order_by(MedioPago.id)
        ).all()
        if not medios:
            raise RuntimeError("No hay medios de pago activos para cobrar las facturas.")

        facturas = db.scalars(
            select(Factura).where(Factura.activo.is_(True)).order_by(Factura.id)
        ).all()
        for factura in facturas:
            pagado = sum(
                (Decimal(str(comprobante.importe)) for comprobante in factura.comprobantes
                 if comprobante.activo),
                Decimal("0"),
            )
            total = Decimal(str(factura.importe_total))
            saldo = (total - pagado).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
            if saldo < 0:
                raise RuntimeError(
                    f"La factura {factura.id} tiene comprobantes por encima de su total."
                )
            if saldo == 0:
                continue
            db.add(
                ComprobantePago(
                    factura_id=factura.id,
                    medio_pago_id=medios[factura.id % len(medios)].id,
                    importe=float(saldo),
                    fecha_hora_emision=factura.fecha_hora_emision,
                )
            )
            creados += 1
        db.commit()

    resumen["comprobantes"] = {"creados": creados}
    return resumen


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Puebla ventas, atenciones y comprobantes de pago."
    )
    parser.add_argument(
        "--anio",
        type=int,
        default=date.today().year,
        help="Año a generar (por defecto, el actual).",
    )
    argumentos = parser.parse_args()

    from src.database import engine

    resumen = poblar_comparativa_atenciones_comprobantes(
        engine, anio=argumentos.anio
    )
    print(f"Datos generados: {resumen}")


if __name__ == "__main__":
    main()
