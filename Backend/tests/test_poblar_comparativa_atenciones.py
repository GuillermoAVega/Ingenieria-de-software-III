from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from scripts.poblar_comparativa_atenciones import poblar_comparativa_atenciones
from src.atencion.models import Atencion
from src.mesa.models import Mesa
from src.database import configurar_sqlite
from src.models import Comanda, Factura
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


def test_base_poblada_permite_crear_una_comanda_inmediata(cliente, motor):
    poblar_comparativa_atenciones(motor, hoy=date.today())

    with Session(motor) as db:
        comandas_abiertas = db.scalars(
            select(Comanda).where(Comanda.estado == "abierta")
        ).all()
        comandas_sin_factura = db.scalars(
            select(Comanda).where(~Comanda.factura.has())
        ).all()
        mesa = db.scalar(
            select(Mesa).where(Mesa.estado.is_(True), Mesa.disponible.is_(True))
        )
        assert len(comandas_abiertas) == 1
        assert comandas_abiertas[0].mesa_ids == [comandas_abiertas[0].mesa_id]
        assert comandas_abiertas[0].mesa.disponible is False
        assert len(comandas_sin_factura) == 2
        assert all(comanda.mesa.disponible is False for comanda in comandas_sin_factura)
        assert db.scalar(select(Factura.id)) is not None
        assert mesa is not None

    respuesta = cliente.post(
        "/comandas",
        json={
            "mesa_ids": [mesa.id],
            "comensales": 1,
        },
    )

    assert respuesta.status_code == 201, respuesta.text
    assert cliente.get(f"/mesas/{mesa.id}").json()["disponible"] is False
