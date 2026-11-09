from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from scripts.poblar_comparativa_atenciones import poblar_comparativa_atenciones
from src.atencion.models import Atencion
from src.database import configurar_sqlite
from src.models import Comanda
from src.mozo.models import Mozo


def test_todas_las_comandas_se_asignan_a_una_atencion_de_su_sector_y_fecha():
    motor = configurar_sqlite(
        create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    )
    hoy = date.today()
    poblar_comparativa_atenciones(motor, anio=hoy.year, hoy=hoy)

    with Session(motor) as db:
        atenciones = db.scalars(
            select(Atencion).where(Atencion.estado.is_(True))
        ).all()
        comandas = db.scalars(select(Comanda)).all()
        mozos = set(db.scalars(select(Mozo.id)).all())
        mozos_con_historial = {
            atencion.mozo_id
            for atencion in atenciones
            if atencion.fecha_hasta is not None
        }

        assert mozos <= mozos_con_historial
        assert comandas
        for comanda in comandas:
            candidatas = [
                atencion
                for atencion in atenciones
                if atencion.sector_id == comanda.mesa.sector_id
                and atencion.fecha_desde <= comanda.fecha
                and (
                    atencion.fecha_hasta is None
                    or comanda.fecha <= atencion.fecha_hasta
                )
            ]
            assert len(candidatas) == 1
            assert comanda.mozo_id == candidatas[0].mozo_id

    motor.dispose()
