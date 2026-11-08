"""Constantes y helpers HTTP compartidos por las pruebas de líneas de factura."""

from datetime import datetime

RUTA = "/detalles-factura"
EMISION = datetime(2026, 6, 15, 13, 0)


def post(cliente, esc, indice=0, cantidad=1, **extra):
    return cliente.post(
        RUTA,
        json={
            "factura_id": esc["factura_id"],
            "detalle_comanda_id": esc["detalles"][indice],
            "cantidad": cantidad,
            **extra,
        },
    )


def total(cliente, factura_id):
    return cliente.get(f"/facturas/{factura_id}").json()["importe_total"]
