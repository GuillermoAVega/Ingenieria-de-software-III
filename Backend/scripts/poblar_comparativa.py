"""Genera ventas de ejemplo de octubre y noviembre del año actual.

Uso (desde `Backend/`):

    venv/bin/python -m scripts.poblar_comparativa
    venv/bin/python -m scripts.poblar_comparativa --anio 2025
    DB_URL=sqlite:////tmp/prueba.db venv/bin/python -m scripts.poblar_comparativa

ATENCIÓN: igual que `scripts.poblar_db`, en cada ejecución ELIMINA y VUELVE A
CREAR todas las tablas del modelo antes de insertar los datos. No usar sobre
una base con información que se quiera conservar.

Reutiliza `poblar_base` para dejar sectores, mesas, mozos, clientes, productos
y promociones coherentes, y luego agrega comandas y facturas cerradas para cada
día de octubre y noviembre hasta la fecha actual. Los importes salen del motor
real de facturación, así que el reporte `comparativa-mensual` muestra series con
variación diaria y una diferencia visible entre ambos meses.
"""

import argparse
import random
import sys
from calendar import monthrange
from datetime import date, datetime, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from scripts.poblar_db import (  # noqa: E402
    _crear_comanda,
    _facturar,
    _mesas_disponibles,
    poblar_base,
)
from src.models import Factura  # noqa: E402

MESES = (10, 11)

PLATOS = (
    "napolitana",
    "muzza",
    "fugazzeta",
    "bife",
    "milanesa",
    "ravioles",
    "noquis",
    "parrillada",
)
BEBIDAS = ("cerveza", "gaseosa", "agua", "limonada", "malbec")
POSTRES = ("flan", "tiramisu", "helado", "panqueque")


def _items_para_ticket(rng: random.Random, productos: dict) -> list:
    """Arma un pedido variado a partir del catálogo ya poblado."""
    items = [
        (productos[rng.choice(PLATOS)], rng.randint(1, 2), None)
        for _ in range(rng.randint(1, 2))
    ]
    for _ in range(rng.randint(1, 2)):
        items.append((productos[rng.choice(BEBIDAS)], rng.randint(1, 3), None))
    if rng.random() < 0.6:
        items.append((productos[rng.choice(POSTRES)], rng.randint(1, 2), None))
    return items


def _tickets_del_dia(rng: random.Random, fecha: date) -> int:
    """Más tickets los fines de semana y en noviembre que en octubre."""
    base = 2 if fecha.month == 10 else 3
    fin_de_semana = fecha.weekday() >= 4
    return base + int(fin_de_semana) + rng.randint(0, 1)


def _agregar_ventas(db: Session, anio: int, ids: dict, hoy: date) -> None:
    mozos = list(ids["mozos"].values())
    mesas = _mesas_disponibles(db)
    if not mesas:
        raise RuntimeError("No hay mesas disponibles para generar las ventas.")
    productos = ids["productos"]

    for mes in MESES:
        for dia in range(1, monthrange(anio, mes)[1] + 1):
            fecha = date(anio, mes, dia)
            if fecha > hoy:
                break
            rng = random.Random(f"{anio}-{mes}-{dia}")
            for ticket in range(_tickets_del_dia(rng, fecha)):
                hora = time(rng.choice((12, 13, 20, 21)), rng.choice((0, 15, 30, 45)))
                comanda = _crear_comanda(
                    db,
                    fecha=fecha,
                    hora=hora,
                    mozo_id=mozos[ticket % len(mozos)],
                    mesa_id=mesas[(dia + ticket) % len(mesas)],
                    items=_items_para_ticket(rng, productos),
                    cerrada=True,
                )
                emision = datetime.combine(fecha, hora)
                _facturar(db, comanda, emision)


def _resumen_ventas(motor: Engine, anio: int) -> dict[str, dict[str, float | int]]:
    """Facturas y total facturado por mes, para el mensaje final."""
    with Session(motor) as db:
        filas = db.execute(
            select(
                func.strftime("%m", Factura.fecha_hora_emision),
                func.count(Factura.id),
                func.sum(Factura.importe_total),
            )
            .where(
                Factura.activo.is_(True),
                func.strftime("%Y", Factura.fecha_hora_emision) == str(anio),
                func.strftime("%m", Factura.fecha_hora_emision).in_(
                    [f"{mes:02d}" for mes in MESES]
                ),
            )
            .group_by(func.strftime("%m", Factura.fecha_hora_emision))
        ).all()
    return {
        str(mes): {"facturas": int(cantidad), "total": round(float(total or 0), 2)}
        for mes, cantidad, total in filas
    }


def poblar_comparativa(
    motor: Engine, anio: int | None = None, hoy: date | None = None
) -> dict[str, dict[str, float | int]]:
    """Recrea la base y agrega ventas hasta hoy en octubre y noviembre de `anio`."""
    hoy = hoy or date.today()
    anio = anio or hoy.year
    ids = poblar_base(motor, hoy=hoy)
    fabrica = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    with fabrica() as db:
        _agregar_ventas(db, anio, ids, hoy)
    return _resumen_ventas(motor, anio)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Puebla la base con ventas de octubre y noviembre de un año."
    )
    parser.add_argument(
        "--anio",
        type=int,
        default=date.today().year,
        help="Año a generar (por defecto, el actual).",
    )
    argumentos = parser.parse_args()

    from src.database import engine

    print(
        "Recreando el esquema y generando ventas en "
        f"{engine.url.render_as_string(hide_password=True)}"
    )
    resumen = poblar_comparativa(engine, anio=argumentos.anio)
    print(
        f"Ventas de octubre y noviembre de {argumentos.anio} "
        f"hasta el {date.today().strftime('%d/%m/%Y')}:"
    )
    for mes in MESES:
        datos = resumen.get(f"{mes:02d}", {"facturas": 0, "total": 0.0})
        print(
            f"  Mes {mes}: {datos['facturas']} facturas, "
            f"total ${datos['total']:,.2f}"
        )


if __name__ == "__main__":
    main()
