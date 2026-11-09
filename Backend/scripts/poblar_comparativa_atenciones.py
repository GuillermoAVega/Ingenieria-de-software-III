"""Puebla la base como `poblar_comparativa` y asigna cada comanda según su atención.

Uso (desde `Backend/`):

    venv/bin/python -m scripts.poblar_comparativa_atenciones
    venv/bin/python -m scripts.poblar_comparativa_atenciones --anio 2025
    DB_URL=sqlite:////tmp/prueba.db venv/bin/python -m scripts.poblar_comparativa_atenciones

Al igual que los otros scripts de población, elimina y vuelve a crear todas las
tablas. No usar sobre una base con información que se quiera conservar.
"""

import argparse
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, select  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from scripts.poblar_comparativa import poblar_comparativa  # noqa: E402
from src.atencion import services as atencion_services  # noqa: E402
from src.atencion.models import Atencion  # noqa: E402
from src.atencion.schema import AtencionCreate, AtencionUpdate  # noqa: E402
from src.models import Comanda  # noqa: E402

DIAS_POR_ASIGNACION = 90


def _crear_atenciones_historicas(
    db: Session, fecha_inicio: date, hoy: date
) -> None:
    """Genera períodos consecutivos para cada sector con sus mozos asignados."""
    atenciones_existentes = db.scalars(select(Atencion).order_by(Atencion.id)).all()
    mozos_por_sector: dict[int, list[int]] = defaultdict(list)
    for atencion in atenciones_existentes:
        if atencion.mozo_id not in mozos_por_sector[atencion.sector_id]:
            mozos_por_sector[atencion.sector_id].append(atencion.mozo_id)

    db.execute(delete(Atencion))
    db.commit()

    for sector_id, mozos in mozos_por_sector.items():
        desde = fecha_inicio
        periodo = 0
        while desde <= hoy:
            hasta = min(desde + timedelta(days=DIAS_POR_ASIGNACION - 1), hoy)
            mozo_id = mozos[periodo % len(mozos)]
            atencion = atencion_services.crear_atencion(
                db,
                AtencionCreate(
                    fecha_desde=desde,
                    mozo_id=mozo_id,
                    sector_id=sector_id,
                ),
            )
            if hasta < hoy:
                atencion_services.modificar_atencion(
                    db, atencion.id, AtencionUpdate(fecha_hasta=hasta)
                )
            desde = hasta + timedelta(days=1)
            periodo += 1


def _asignar_comandas_a_atenciones(db: Session) -> int:
    """Asigna cada comanda al mozo atendiendo el sector de su mesa en esa fecha."""
    atenciones_por_sector: dict[int, list[Atencion]] = defaultdict(list)
    for atencion in db.scalars(
        select(Atencion)
        .where(Atencion.estado.is_(True))
        .order_by(Atencion.fecha_desde, Atencion.id)
    ):
        atenciones_por_sector[atencion.sector_id].append(atencion)

    comandas = db.scalars(select(Comanda).order_by(Comanda.id)).all()
    for comanda in comandas:
        sector_id = comanda.mesa.sector_id
        candidatas = [
            atencion
            for atencion in atenciones_por_sector.get(sector_id, [])
            if atencion.fecha_desde <= comanda.fecha
            and (atencion.fecha_hasta is None or comanda.fecha <= atencion.fecha_hasta)
        ]
        if len(candidatas) != 1:
            raise RuntimeError(
                f"La comanda {comanda.id} del {comanda.fecha} no tiene una única "
                f"atención para el sector {sector_id}."
            )
        comanda.mozo_id = candidatas[0].mozo_id

    db.commit()
    return len(comandas)


def poblar_comparativa_atenciones(
    motor: Engine, anio: int | None = None, hoy: date | None = None
) -> dict[str, dict[str, float | int]]:
    """Recrea los datos de comparativa con atenciones históricas y comandas asignadas."""
    hoy = hoy or date.today()
    anio = anio or hoy.year
    resumen = poblar_comparativa(motor, anio=anio, hoy=hoy)
    fecha_inicio = min(date(hoy.year - 1, 1, 1), date(anio, 10, 1))

    fabrica = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    with fabrica() as db:
        _crear_atenciones_historicas(db, fecha_inicio, hoy)
        _asignar_comandas_a_atenciones(db)
    return resumen


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Puebla ventas de octubre y noviembre con atenciones históricas "
            "asignadas a sus comandas."
        )
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
    resumen = poblar_comparativa_atenciones(engine, anio=argumentos.anio)
    print(
        f"Ventas de octubre y noviembre de {argumentos.anio} "
        f"hasta el {date.today().strftime('%d/%m/%Y')}:"
    )
    for mes in (10, 11):
        datos = resumen.get(f"{mes:02d}", {"facturas": 0, "total": 0.0})
        print(
            f"  Mes {mes}: {datos['facturas']} facturas, "
            f"total ${datos['total']:,.2f}"
        )


if __name__ == "__main__":
    main()
