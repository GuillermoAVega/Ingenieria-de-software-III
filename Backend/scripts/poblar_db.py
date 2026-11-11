"""Puebla la base de datos con datos de ejemplo de un restaurante argentino.

Uso (desde `Backend/`):

    venv/bin/python -m scripts.poblar_db
    DB_URL=sqlite:////tmp/prueba.db venv/bin/python -m scripts.poblar_db

ATENCIÓN: en cada ejecución ELIMINA y VUELVE A CREAR todas las tablas del
modelo (`drop_all` + `create_all`) antes de insertar los datos, por lo que
cualquier dato previo de la base apuntada por `DB_URL` se pierde.

Usa el mismo motor que la app (`src.database`, variable `DB_URL` de
`Backend/.env`; se puede sobrescribir por entorno para usar una base
descartable). Las fechas son relativas a `date.today()`, de modo que las
promociones y los combos quedan vigentes, vencidos o futuros al ejecutarlo.

Siempre que existe un servicio se reutiliza (altas, bajas, reservas, detección
de promociones); las facturas se calculan con el motor agrupado del backend
(`recalcular_producto`), así que `precio_unitario`, `promocion_id`,
`unidades_gratis`, `precio_final` e `importe_total` son consistentes con él.
"""

import random
import sys
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# Permite también `python scripts/poblar_db.py` (agrega Backend/ al path)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import MetaData, select  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from src.atencion import services as atencion_services  # noqa: E402
from src.atencion.schema import AtencionCreate, AtencionUpdate  # noqa: E402
from src.cliente import services as cliente_services  # noqa: E402
from src.cliente.schemas import ClienteCreate  # noqa: E402
from src.comanda.services import (  # noqa: E402
    liberar_mesas,
    obtener_mesas_disponibles,
    ocupar_mesas,
)
from src.detalleReserva import models as detalle_reserva_models  # noqa: E402,F401
from src.mesa import services as mesa_services  # noqa: E402
from src.mesa.models import Mesa  # noqa: E402
from src.mesa.schemas import MesaCreate  # noqa: E402
from src.models import (  # noqa: E402
    Comanda,
    ComprobantePago,
    DetalleComanda,
    DetalleFactura,
    Factura,
    MedioPago,
    ModeloBase,
)
from src.mozo import services as mozo_services  # noqa: E402
from src.mozo.schema import MozoCreate  # noqa: E402

# `registro` y `promociones.models` cargan los mappers antes del create_all
from src.productos import registro  # noqa: E402,F401
from src.productos import services as productos_services  # noqa: E402
from src.productos.bebidas import services as bebidas_services  # noqa: E402
from src.productos.bebidas.schemas import BebidaCrear  # noqa: E402
from src.productos.combos import services as combos_services  # noqa: E402
from src.productos.combos.schemas import ComboCrear  # noqa: E402
from src.productos.menus_del_dia import services as menus_del_dia_services  # noqa: E402
from src.productos.menus_del_dia.schemas import MenuDelDiaCrear  # noqa: E402
from src.productos.menus_ejecutivos import services as menus_services  # noqa: E402
from src.productos.menus_ejecutivos.schemas import MenuCrear  # noqa: E402
from src.productos.platos import services as platos_services  # noqa: E402
from src.productos.platos.schemas import PlatoCrear  # noqa: E402
from src.productos.postres import services as postres_services  # noqa: E402
from src.productos.postres.schemas import PostreCrear  # noqa: E402
from src.productos_menu import services as productos_menu_services  # noqa: E402
from src.productos_menu.schemas import ProductoMenuCrear  # noqa: E402
from src.promociones import models as promociones_models  # noqa: E402,F401
from src.promociones import services as promociones_services  # noqa: E402
from src.promociones.models import Promocion  # noqa: E402
from src.promociones.schemas import PromocionCrear  # noqa: E402
from src.reserva import services as reserva_services  # noqa: E402
from src.reserva.estados import EstadoReserva  # noqa: E402
from src.reserva.schemas import ReservaCreate  # noqa: E402
from src.secciones import services as secciones_services  # noqa: E402
from src.secciones.schemas import SeccionCrear  # noqa: E402
from src.sector import services as sector_services  # noqa: E402
from src.sector.schema import SectorCreate  # noqa: E402
from src.utils import exigir_producto_activo  # noqa: E402

CENTAVOS = Decimal("0.01")


# --------------------------------------------------------------------- estructura


def _crear_sectores_y_mesas(db: Session) -> dict:
    """Sectores y mesas de capacidades variadas; devuelve ids por clave."""
    sectores = {}
    for clave, nombre, fumadores, piso in (
        ("salon", "Salón principal", False, "Planta baja"),
        ("terraza", "Terraza", True, "Planta baja"),
        ("piso1", "Primer piso", False, "Primer piso"),
        ("barra", "Barra", False, "Planta baja"),
    ):
        sectores[clave] = sector_services.crear_sector(
            db, SectorCreate(nombre=nombre, apto_fumadores=fumadores, piso=piso)
        ).id

    # (clave, sector, capacidad, disponible)
    definicion_mesas = (
        ("s1", "salon", 2, True),
        ("s2", "salon", 2, True),
        ("s3", "salon", 4, True),
        ("s4", "salon", 4, True),
        ("s5", "salon", 6, True),
        ("t1", "terraza", 4, True),
        ("t2", "terraza", 4, True),
        ("t3", "terraza", 8, True),
        ("p1", "piso1", 6, True),
        ("p2", "piso1", 10, True),
        ("b1", "barra", 2, True),
        ("b2", "barra", 2, False),  # fuera de servicio por mantenimiento
    )
    mesas = {}
    for clave, sector, capacidad, disponible in definicion_mesas:
        mesas[clave] = mesa_services.crear_mesa(
            db,
            MesaCreate(
                capacidad=capacidad, disponible=disponible, sector_id=sectores[sector]
            ),
        ).id
    return {"sectores": sectores, "mesas": mesas}


def _crear_personal(db: Session, hoy: date, sectores: dict) -> dict:
    """Mozos con sus atenciones (asignación a sectores) abiertas y una cerrada."""
    mozos = {}
    for clave, nombre, legajo in (
        ("carlos", "Carlos Benítez", 1001),
        ("lucia", "Lucía Fernández", 1002),
        ("martin", "Martín Sosa", 1003),
        ("romina", "Romina Acosta", 1004),
    ):
        mozos[clave] = mozo_services.crear_mozo(
            db, MozoCreate(nombre=nombre, nro_legajo=legajo)
        ).id

    asignaciones = (
        ("carlos", "salon"),
        ("lucia", "salon"),
        ("martin", "terraza"),
        ("romina", "piso1"),
        ("romina", "barra"),
    )
    for mozo, sector in asignaciones:
        atencion_services.crear_atencion(
            db,
            AtencionCreate(
                fecha_desde=hoy - timedelta(days=90),
                mozo_id=mozos[mozo],
                sector_id=sectores[sector],
            ),
        )
    # Asignación histórica ya finalizada (Martín atendía antes la barra)
    historica = atencion_services.crear_atencion(
        db,
        AtencionCreate(
            fecha_desde=hoy - timedelta(days=200),
            mozo_id=mozos["martin"],
            sector_id=sectores["barra"],
        ),
    )
    atencion_services.modificar_atencion(
        db,
        historica.id,
        AtencionUpdate(fecha_hasta=hoy - timedelta(days=100)),
    )
    return mozos


def _crear_clientes(db: Session) -> dict:
    clientes = {}
    for clave, dni, nombre, apellido, telefono in (
        ("ana", "30123456", "Ana", "Gómez", "11-5555-1234"),
        ("bruno", "28456789", "Bruno", "Ledesma", "11-4444-9876"),
        ("carla", "35789012", "Carla", "Domínguez", "351-555-0101"),
        ("diego", "27345678", "Diego", "Quiroga", "341-555-0202"),
        ("elena", "32987654", "Elena", "Paz", "11-6666-3030"),
        ("facundo", "38654321", "Facundo", "Ibarra", "261-555-0404"),
        ("gabriela", "29111222", "Gabriela", "Méndez", "11-7777-5050"),
        ("hugo", "24333444", "Hugo", "Rivas", "223-555-0606"),
    ):
        clientes[clave] = cliente_services.crear_cliente(
            db,
            ClienteCreate(dni=dni, nombre=nombre, apellido=apellido, telefono=telefono),
        ).id
    return clientes


def _crear_medios_pago(db: Session) -> dict:
    medios = {}
    for clave, descripcion in (
        ("efectivo", "Efectivo"),
        ("debito", "Tarjeta de débito"),
        ("credito", "Tarjeta de crédito"),
        ("mercadopago", "Mercado Pago"),
        ("transferencia", "Transferencia bancaria"),
    ):
        medio = MedioPago(descripcion=descripcion)
        db.add(medio)
        db.flush()
        medios[clave] = medio.id
    db.commit()
    return medios


# ---------------------------------------------------------------------- productos


def _crear_catalogo(db: Session, hoy: date) -> dict:
    """Secciones, platos, bebidas, postres, menús, combos, menú del día y una baja."""
    secciones = {}
    for posicion, (clave, nombre, subtitulo) in enumerate(
        (
            ("entradas", "Entradas", "Para compartir"),
            ("pizzas", "Pizzas", "A la piedra"),
            ("carnes", "Carnes y parrilla", "Cortes de la casa"),
            ("pastas", "Pastas", "Caseras"),
            ("bebidas", "Bebidas", None),
            ("postres", "Postres", "Dulces de la casa"),
            ("menus", "Menús y combos", "Opciones con ahorro"),
        ),
        start=1,
    ):
        secciones[clave] = secciones_services.crear_seccion(
            db, SeccionCrear(nombre=nombre, subtitulo=subtitulo, posicion=posicion)
        ).id

    p = {}  # ids de productos por clave

    for clave, nombre, precio, desc, seccion, personas in (
        ("provoleta", "Provoleta a la parrilla", "8500", "Con orégano y ají molido", "entradas", 2),
        ("empanada", "Empanada de carne cortada a cuchillo", "2200", "Unidad, horno de barro", "entradas", 1),
        ("muzza", "Pizza muzzarella", "11000", "Salsa de tomate y muzzarella", "pizzas", 2),
        ("fugazzeta", "Pizza fugazzeta", "12500", "Cebolla y muzzarella", "pizzas", 2),
        ("napolitana", "Pizza napolitana", "13500", "Tomate, ajo y albahaca", "pizzas", 2),
        ("bife", "Bife de chorizo", "18500", "400 g con guarnición a elección", "carnes", 1),
        ("milanesa", "Milanesa napolitana con papas fritas", "15800", None, "carnes", 1),
        ("parrillada", "Parrillada para dos", "42000", "Asado, vacío, chorizo, morcilla y provoleta", "carnes", 2),
        ("ravioles", "Ravioles de ricota con salsa mixta", "13200", None, "pastas", 1),
        ("noquis", "Ñoquis de papa con bolognesa", "12400", None, "pastas", 1),
        ("lasagna", "Lasagna de verduras", "13900", "Retirada de la carta", "pastas", 1),
    ):
        p[clave] = platos_services.crear_plato(
            db,
            PlatoCrear(
                nombre=nombre,
                precio=Decimal(precio),
                descripcion=desc,
                seccion_id=secciones[seccion],
                cant_personas=personas,
            ),
        ).id

    for clave, nombre, precio, desc, alcoholica in (
        ("gaseosa", "Coca-Cola 500 ml", "2800", None, False),
        ("agua", "Agua mineral sin gas 500 ml", "2200", None, False),
        ("cerveza", "Cerveza Quilmes 1 L", "4800", "Botella", True),
        ("malbec", "Vino Malbec (copa)", "4200", "Bodega mendocina", True),
        ("limonada", "Limonada con menta y jengibre", "3500", None, False),
    ):
        p[clave] = bebidas_services.crear_bebida(
            db,
            BebidaCrear(
                nombre=nombre,
                precio=Decimal(precio),
                descripcion=desc,
                seccion_id=secciones["bebidas"],
                es_alcoholica=alcoholica,
            ),
        ).id

    for clave, nombre, precio, desc in (
        ("flan", "Flan casero con dulce de leche", "5200", "Con crema"),
        ("tiramisu", "Tiramisú", "6200", None),
        ("helado", "Helado artesanal (3 bochas)", "5800", "Sabores del día"),
        ("panqueque", "Panqueque de dulce de leche", "5500", "Flambeado"),
    ):
        p[clave] = postres_services.crear_postre(
            db,
            PostreCrear(
                nombre=nombre,
                precio=Decimal(precio),
                descripcion=desc,
                seccion_id=secciones["postres"],
            ),
        ).id

    # Menús ejecutivos: un plato y un postre cada uno
    for clave, nombre, precio, plato, postre in (
        ("menu_milanesa", "Menú ejecutivo milanesa", "17500", "milanesa", "flan"),
        ("menu_pasta", "Menú ejecutivo pasta", "15900", "noquis", "helado"),
    ):
        p[clave] = menus_services.crear_menu(
            db,
            MenuCrear(
                nombre=nombre,
                precio=Decimal(precio),
                descripcion="Plato principal y postre",
                seccion_id=secciones["menus"],
                plato_id=p[plato],
                postre_id=p[postre],
            ),
        ).id

    # Combos vigentes (el servicio exige fecha_hasta >= hoy)
    p["combo_pizza"] = combos_services.crear_combo(
        db,
        ComboCrear(
            nombre="Combo pizza y cerveza",
            precio=Decimal("14500"),
            descripcion="Pizza muzzarella + cerveza de 1 L",
            seccion_id=secciones["menus"],
            fecha_desde=hoy - timedelta(days=10),
            fecha_hasta=hoy + timedelta(days=60),
            platos=[{"id": p["muzza"], "cantidad": 2}],
            bebidas=[{"id": p["cerveza"], "cantidad": 1}],
            postres=[],
        ),
        hoy,
    ).id
    p["combo_parrilla"] = combos_services.crear_combo(
        db,
        ComboCrear(
            nombre="Combo parrilla completa",
            precio=Decimal("52000"),
            descripcion="Parrillada para dos, vino y dos postres",
            seccion_id=secciones["menus"],
            fecha_desde=hoy - timedelta(days=5),
            fecha_hasta=hoy + timedelta(days=90),
            platos=[{"id": p["parrillada"], "cantidad": 1}],
            bebidas=[{"id": p["malbec"], "cantidad": 1}],
            postres=[{"id": p["flan"], "cantidad": 2}, {"id": p["helado"], "cantidad": 1}],
        ),
        hoy,
    ).id

    # Menús del día: productos propios; cada uno se asigna a una fecha (hoy o futura)
    for dias, nombre, precio in (
        (0, "Menú del día: milanesa con papas", "9800"),
        (1, "Menú del día: ñoquis con salsa", "9200"),
        (2, "Menú del día: bife con ensalada", "11500"),
        (3, "Menú del día: ravioles con crema", "10200"),
    ):
        menu_del_dia = menus_del_dia_services.crear_menu_del_dia(
            db,
            MenuDelDiaCrear(
                nombre=nombre,
                precio=Decimal(precio),
                descripcion="Plato del día con bebida",
                seccion_id=secciones["menus"],
            ),
        )
        productos_menu_services.crear_producto_menu(
            db,
            ProductoMenuCrear(
                menu_del_dia_id=menu_del_dia.id, fecha=hoy + timedelta(days=dias)
            ),
            hoy,
        )

    # Producto dado de baja (nadie lo usa, así que la baja no está restringida)
    productos_services.dar_de_baja(db, registro.Plato, p["lasagna"], hoy)

    return {"secciones": secciones, "productos": p}


# ------------------------------------------------------------------- promociones


def _crear_promociones(db: Session, hoy: date, p: dict) -> dict:
    """Promociones de ambos tipos y en distintos estados; cubren la selección por mayor ahorro."""

    def d(dias: int) -> date:
        return hoy + timedelta(days=dias)

    def alta(nombre, desde, hasta, descuento, claves) -> Promocion:
        return promociones_services.crear_promocion(
            db,
            PromocionCrear(
                nombre=nombre,
                tipo="porcentaje",
                fecha_desde=desde,
                fecha_hasta=hasta,
                descuento=Decimal(descuento),
                productos_ids=[p[c] for c in claves],
            ),
            hoy,
        )

    def alta_lleva_paga(nombre, desde, hasta, lleva, paga, claves) -> Promocion:
        return promociones_services.crear_promocion(
            db,
            PromocionCrear(
                nombre=nombre,
                tipo="lleva_paga",
                fecha_desde=desde,
                fecha_hasta=hasta,
                lleva=lleva,
                paga=paga,
                productos_ids=[p[c] for c in claves],
            ),
            hoy,
        )

    promos = {}
    # Vigente: 10 % en las tres pizzas
    promos["pizzas"] = alta(
        "Pizzas al 10%", d(-15), d(30), "10", ["muzza", "fugazzeta", "napolitana"]
    )
    # Vigente y solapada en la napolitana con MAYOR descuento: debe ganar esta
    promos["napolitana"] = alta(
        "Napolitana especial 20%", d(-10), d(10), "20", ["napolitana"]
    )
    # Empate de descuento sobre el bife: gana la de menor id (la primera)
    promos["bife_a"] = alta("Bife de chorizo 15% (A)", d(-7), d(20), "15", ["bife"])
    promos["bife_b"] = alta("Noche de carnes 15% (B)", d(-3), d(15), "15", ["bife"])
    # Futura
    promos["pastas_futura"] = alta(
        "Semana de las pastas 30%", d(15), d(22), "30", ["ravioles", "noquis"]
    )
    # Dada de baja (vigente por fechas, pero no aplicable)
    promos["bebidas_baja"] = alta("Bebidas al 50%", d(-5), d(25), "50", ["gaseosa"])
    promociones_services.dar_de_baja_promocion(db, promos["bebidas_baja"].id)
    # Incluye un combo
    promos["combo"] = alta(
        "Combo parrilla 12%", d(-5), d(60), "12", ["combo_parrilla"]
    )

    # 2x1 y 10 % sobre las empanadas: compiten por mayor ahorro en pesos según la
    # cantidad (4 unidades -> gana la 2x1; 1 unidad -> la 2x1 ahorra 0 y gana el 10 %)
    promos["empanadas_10"] = alta("Empanadas 10%", d(-15), d(30), "10", ["empanada"])
    promos["empanadas_2x1"] = alta_lleva_paga(
        "Empanadas 2x1", d(-15), d(30), 2, 1, ["empanada"]
    )
    # 3x2 en limonadas
    promos["limonada_3x2"] = alta_lleva_paga(
        "Limonadas 3x2", d(-15), d(30), 3, 2, ["limonada"]
    )

    # Vencida: el servicio rechaza altas con fecha_hasta pasada, así que se
    # inserta directo (equivale a una promoción que venció con el tiempo)
    vencida = Promocion(
        nombre="Promo verano 25%",
        tipo="porcentaje",
        fecha_desde=d(-60),
        fecha_hasta=d(-30),
        descuento=Decimal("25"),
        productos=[db.get(registro.Plato, p["ravioles"]), db.get(registro.Plato, p["noquis"])],
    )
    db.add(vencida)
    db.commit()
    promos["vencida"] = vencida

    return {clave: promo.id for clave, promo in promos.items()}


# ----------------------------------------------------------------------- reservas


def _crear_reservas(db: Session, hoy: date, ids: dict) -> dict:
    """Reservas pasadas y futuras sin superposición de mesa, fecha y hora."""
    c, m, p = ids["clientes"], ids["mesas"], ids["productos"]

    def reservar(fecha, hora, comensales, cliente, mesas, obs=None, detalles=None):
        return reserva_services.crear_reserva(
            db,
            ReservaCreate(
                fecha=fecha,
                hora=hora,
                cant_comensales=comensales,
                observaciones=obs,
                cliente_id=c[cliente],
                mesa_ids=[m[x] for x in mesas],
                detalles=detalles or [],
            ),
        )

    reservas = {}
    # Pasadas: una asistió (con comanda), una ausente y una cancelada
    reservas["asistio"] = reservar(
        hoy - timedelta(days=7), time(21, 0), 4, "ana", ["s3"], "Cumpleaños"
    )
    reservas["ausente"] = reservar(
        hoy - timedelta(days=5), time(20, 30), 2, "bruno", ["s1"]
    )
    reservas["ausente_carla"] = reservar(
        hoy - timedelta(days=20), time(21, 0), 3, "carla", ["p1"]
    )
    reservas["ausente_diego"] = reservar(
        hoy - timedelta(days=30), time(13, 30), 2, "diego", ["p2"]
    )
    reservas["ausente_hugo"] = reservar(
        hoy - timedelta(days=45), time(20, 0), 5, "hugo", ["t3"]
    )
    reservas["cancelada"] = reservar(
        hoy - timedelta(days=3), time(13, 0), 6, "carla", ["s5"], "Almuerzo familiar"
    )
    # Hoy y futuras
    reservas["hoy"] = reservar(hoy, time(21, 0), 4, "diego", ["t1"])
    reservas["manana"] = reservar(
        hoy + timedelta(days=1),
        time(20, 0),
        6,
        "elena",
        ["p1"],
        "Pidió la pizza napolitana por adelantado",
        [{"producto_id": p["napolitana"], "cantidad_producto": 2}],
    )
    # Grupo grande: dos mesas cuya capacidad suma 12 (8 + 4)
    reservas["grupo"] = reservar(
        hoy + timedelta(days=5),
        time(21, 30),
        11,
        "facundo",
        ["t3", "t2"],
        "Cena de egresados, sector fumadores",
        [{"producto_id": p["parrillada"], "cantidad_producto": 3}],
    )
    # Misma mesa, otro horario (permitido)
    reservas["misma_mesa"] = reservar(
        hoy + timedelta(days=1), time(22, 30), 2, "gabriela", ["t1"]
    )
    reservas["salon"] = reservar(
        hoy + timedelta(days=10), time(13, 30), 10, "hugo", ["p2"], "Reunión de trabajo"
    )

    # Estados finales de las reservas pasadas (no hay servicio para esto)
    reservas["asistio"].estado = EstadoReserva.CON_COMANDA
    reservas["ausente"].estado = EstadoReserva.AUSENTE
    reservas["ausente_carla"].estado = EstadoReserva.AUSENTE
    reservas["ausente_diego"].estado = EstadoReserva.AUSENTE
    reservas["ausente_hugo"].estado = EstadoReserva.AUSENTE
    # `cancelar_reserva` rechaza fechas pasadas, por eso se asigna el estado directo
    reservas["cancelada"].estado = EstadoReserva.CANCELADA
    db.commit()
    return {clave: r.id for clave, r in reservas.items()}


# -------------------------------------------------------------- comandas y facturas


def _mesas_disponibles(db: Session) -> list[int]:
    return db.scalars(
        select(Mesa.id).where(Mesa.estado.is_(True), Mesa.disponible.is_(True))
    ).all()


def _crear_comanda(
    db: Session,
    *,
    fecha: date,
    hora: time,
    mozo_id: int,
    mesa_id: int,
    items: list,
    cliente_id: int | None = None,
    reserva_id: int | None = None,
    cerrada: bool = False,
    entregado: bool = True,
) -> Comanda:
    """Replica `POST /comandas`: los productos deben existir y estar activos."""
    mesas = obtener_mesas_disponibles(db, [mesa_id])
    comanda = Comanda(
        fecha=fecha,
        hora=hora,
        mozo_id=mozo_id,
        mesa_id=mesa_id,
        cliente_id=cliente_id,
        reserva_id=reserva_id,
        mesas_asociadas=mesas,
    )
    detalles = []
    for producto_id, cantidad, observaciones in items:
        exigir_producto_activo(db, producto_id)
        detalles.append(
            DetalleComanda(
                producto_id=producto_id,
                cantidad=cantidad,
                observaciones=observaciones,
                entregado=entregado,
            )
        )
    comanda.detalles = detalles
    ocupar_mesas(mesas)
    db.add(comanda)
    db.commit()
    if cerrada:
        # El router solo permite cerrar con al menos un producto activo
        comanda.estado = "cerrada"
        db.commit()
    return comanda


def _facturar(db: Session, comanda: Comanda, emision: datetime) -> Factura:
    """Factura la comanda como `POST /detalles-factura`: una línea por detalle activo.

    Cada línea toma el precio unitario del producto; luego `recalcular_producto`
    decide por grupo la promoción ganadora (mayor ahorro en pesos, ante empate
    menor id), `unidades_gratis` y `precio_final`, y se suma el `importe_total`.
    """
    factura = Factura(comanda_id=comanda.id, fecha_hora_emision=emision, importe_total=0)
    db.add(factura)
    liberar_mesas(list(comanda.mesas_asociadas))
    db.commit()
    productos_ids = set()
    for dc in comanda.detalles:
        if not dc.activo:
            continue
        precio = float(dc.producto.precio)
        db.add(
            DetalleFactura(
                factura_id=factura.id,
                detalle_comanda_id=dc.id,
                cantidad=dc.cantidad,
                precio_unitario=precio,
                precio_final=float(Decimal(str(precio)) * dc.cantidad),
            )
        )
        productos_ids.add(dc.producto_id)
    db.flush()
    for producto_id in sorted(productos_ids):
        promociones_services.recalcular_producto(db, factura, producto_id)
    db.flush()
    db.refresh(factura)
    total = sum((Decimal(str(d.precio_final)) for d in factura.detalles if d.activo), Decimal(0))
    factura.importe_total = float(total.quantize(CENTAVOS, rounding=ROUND_HALF_UP))
    db.commit()
    db.refresh(factura)
    return factura


def _cobrar(db: Session, factura: Factura, pagos: list) -> None:
    """Registra comprobantes cuya suma es exactamente el total de la factura.

    `pagos` es una lista de (medio_pago_id, fraccion); el último absorbe el
    resto para que la suma no difiera del total por redondeo.
    """
    total = Decimal(str(factura.importe_total))
    acumulado = Decimal(0)
    for i, (medio_id, fraccion) in enumerate(pagos):
        if i == len(pagos) - 1:
            importe = total - acumulado
        else:
            importe = (total * Decimal(str(fraccion))).quantize(
                CENTAVOS, rounding=ROUND_HALF_UP
            )
        acumulado += importe
        db.add(
            ComprobantePago(
                factura_id=factura.id,
                medio_pago_id=medio_id,
                importe=float(importe),
                fecha_hora_emision=factura.fecha_hora_emision,
            )
        )
    db.commit()


def _crear_comandas_y_facturas(db: Session, hoy: date, ids: dict) -> None:
    m, mozos, c = ids["mesas"], ids["mozos"], ids["clientes"]
    p, mp, reservas = ids["productos"], ids["medios_pago"], ids["reservas"]

    # 1) Cena con reserva de hace una semana: pizzas (la napolitana toma el 20 %
    #    por ser la de mayor descuento), cerveza sin promoción, postres, 4 empanadas
    #    (gana la 2x1 frente al 10 %) y 3 limonadas (3x2)
    hace_7 = hoy - timedelta(days=7)
    comanda1 = _crear_comanda(
        db,
        fecha=hace_7,
        hora=time(21, 10),
        mozo_id=mozos["carlos"],
        mesa_id=m["s3"],
        cliente_id=c["ana"],
        reserva_id=reservas["asistio"],
        items=[
            (p["napolitana"], 2, "Una sin albahaca"),
            (p["muzza"], 1, None),
            (p["cerveza"], 2, None),
            (p["flan"], 2, None),
            (p["empanada"], 4, None),
            (p["limonada"], 3, None),
        ],
        cerrada=True,
    )
    factura1 = _facturar(db, comanda1, datetime.combine(hace_7, time(23, 15)))
    _cobrar(db, factura1, [(mp["efectivo"], 0.5), (mp["debito"], 0.5)])

    # 2) Almuerzo de hoy: bife (empate 15 % -> promoción de menor id), combo con
    #    promoción propia, gaseosa (promoción dada de baja), ravioles (promo
    #    vencida y futura: sin descuento) y 1 empanada (gana el 10 %, la 2x1 ahorra 0)
    comanda2 = _crear_comanda(
        db,
        fecha=hoy,
        hora=time(13, 0),
        mozo_id=mozos["lucia"],
        mesa_id=m["s5"],
        items=[
            (p["bife"], 2, "Punto medio"),
            (p["combo_parrilla"], 1, None),
            (p["gaseosa"], 2, None),
            (p["ravioles"], 1, None),
            (p["empanada"], 1, None),
        ],
        cerrada=True,
    )
    factura2 = _facturar(db, comanda2, datetime.combine(hoy, time(14, 40)))
    _cobrar(db, factura2, [(mp["mercadopago"], 1)])

    # 3) Cerrada de ayer, pendiente de facturar
    _crear_comanda(
        db,
        fecha=hoy - timedelta(days=1),
        hora=time(20, 45),
        mozo_id=mozos["martin"],
        mesa_id=m["t2"],
        cliente_id=c["gabriela"],
        items=[(p["menu_milanesa"], 2, None), (p["limonada"], 2, None)],
        cerrada=True,
    )

    # 4) Comanda abierta en curso, con productos aún sin entregar
    _crear_comanda(
        db,
        fecha=hoy,
        hora=time(20, 30),
        mozo_id=mozos["romina"],
        mesa_id=m["p1"],
        cliente_id=c["elena"],
        items=[
            (p["provoleta"], 1, None),
            (p["fugazzeta"], 2, None),
            (p["malbec"], 2, None),
        ],
        entregado=False,
    )


# Rango (mínimo, máximo) de ventas por día de la semana (lunes = 0)
VENTAS_POR_DIA_SEMANA = {0: (0, 1), 1: (0, 1), 2: (0, 2), 3: (0, 2), 4: (1, 3), 5: (2, 4), 6: (1, 3)}
# Meses de temporada alta (vacaciones de invierno y fiestas): una venta extra por día
MESES_TEMPORADA_ALTA = {7, 12}


def _crear_historial_ventas(db: Session, hoy: date, ids: dict) -> None:
    """Ventas cobradas desde el 1/1 del año anterior hasta ayer, para el reporte de ventas.

    Es determinista (semilla fija) y usa productos que no intervienen en los casos
    de promociones de `_crear_comandas_y_facturas`. Incluye casos que el reporte
    no cuenta: facturas sin cobrar, anuladas y con el comprobante anulado.
    """
    azar = random.Random(2026)
    mozos, p, mp = ids["mozos"], ids["productos"], ids["medios_pago"]
    mesas = _mesas_disponibles(db)
    if not mesas:
        raise RuntimeError("No hay mesas disponibles para generar el historial.")
    personal, medios = list(mozos.values()), list(mp.values())
    productos = [p[clave] for clave in ("muzza", "cerveza", "flan", "provoleta", "fugazzeta", "malbec")]

    dia, numero = date(hoy.year - 1, 1, 1), 0
    while dia < hoy:
        minimo, maximo = VENTAS_POR_DIA_SEMANA[dia.weekday()]
        extra = 1 if dia.month in MESES_TEMPORADA_ALTA else 0
        for _ in range(azar.randint(minimo, maximo) + extra):
            numero += 1
            hora = time(azar.choice((12, 13, 14, 20, 21, 22)), azar.choice((0, 15, 30, 45)))
            comanda = _crear_comanda(
                db,
                fecha=dia,
                hora=hora,
                mozo_id=azar.choice(personal),
                mesa_id=azar.choice(mesas),
                items=[(producto, azar.randint(1, 3), None) for producto in azar.sample(productos, 2)],
                cerrada=True,
            )
            emision = datetime.combine(dia, hora) + timedelta(hours=1)
            factura = _facturar(db, comanda, emision)
            if numero % 25 == 0:
                continue  # Factura pendiente de cobro: no es venta
            _cobrar(db, factura, [(azar.choice(medios), 1)])
            if numero % 40 == 0:
                factura.activo = False  # Factura anulada después de cobrarla
            elif numero % 55 == 0:
                factura.comprobantes[0].activo = False  # Comprobante anulado
            db.commit()
        dia += timedelta(days=1)


# ----------------------------------------------------------------------- principal


def poblar_base(motor: Engine, hoy: date | None = None) -> dict:
    """Elimina y recrea el esquema en `motor` y lo puebla; devuelve ids por clave.

    `motor` debe tener las claves foráneas activas (`configurar_sqlite`); el
    motor de `src.database` ya las tiene.
    """
    from src.auth import models as auth_models  # noqa: F401

    hoy = hoy or date.today()
    # Se reflejan las tablas reales de la base: así también se eliminan las
    # sobrantes de otras ramas (p. ej. `menu_del_dia`), que bloquearían el drop
    # por sus claves foráneas hacia `producto`
    existentes = MetaData()
    existentes.reflect(bind=motor)
    existentes.drop_all(bind=motor)
    ModeloBase.metadata.create_all(bind=motor)

    fabrica = sessionmaker(autocommit=False, autoflush=False, bind=motor)
    with fabrica() as db:
        ids = _crear_sectores_y_mesas(db)
        ids["mozos"] = _crear_personal(db, hoy, ids["sectores"])
        ids["clientes"] = _crear_clientes(db)
        ids["medios_pago"] = _crear_medios_pago(db)
        catalogo = _crear_catalogo(db, hoy)
        ids["secciones"] = catalogo["secciones"]
        ids["productos"] = catalogo["productos"]
        ids["promociones"] = _crear_promociones(db, hoy, ids["productos"])
        ids["reservas"] = _crear_reservas(db, hoy, ids)
        _crear_comandas_y_facturas(db, hoy, ids)
        _crear_historial_ventas(db, hoy, ids)
    from src.auth.services import crear_usuarios_iniciales

    crear_usuarios_iniciales(motor)
    return ids


def resumen(motor: Engine) -> dict[str, int]:
    """Cantidad de filas por entidad (para el mensaje final y las pruebas)."""
    tablas = (
        ("Sectores", "sectores"),
        ("Mesas", "mesas"),
        ("Mozos", "mozos"),
        ("Atenciones", "atenciones"),
        ("Clientes", "clientes"),
        ("Medios de pago", "medio_pago"),
        ("Secciones", "seccion"),
        ("Productos (total)", "producto"),
        ("  Platos", "plato"),
        ("  Bebidas", "bebida"),
        ("  Postres", "postre"),
        ("  Menús ejecutivos", "menu_ejecutivo"),
        ("  Combos", "combo_promocion"),
        ("Menú del día", "producto_menu"),
        ("Promociones", "promocion"),
        ("Reservas", "reservas"),
        ("Comandas", "comanda"),
        ("Detalles de comanda", "detalle_comanda"),
        ("Facturas", "factura"),
        ("Detalles de factura", "detalle_factura"),
        ("Comprobantes de pago", "comprobante_pago"),
    )
    cuentas = {}
    with motor.connect() as conexion:
        for etiqueta, tabla in tablas:
            cuentas[etiqueta] = conexion.exec_driver_sql(
                f"SELECT COUNT(*) FROM {tabla}"
            ).scalar_one()
    return cuentas


def main() -> None:
    from src.database import engine

    print(f"Recreando el esquema y poblando: {engine.url.render_as_string(hide_password=True)}")
    poblar_base(engine)
    print("Base de datos poblada. Resumen:")
    for etiqueta, cantidad in resumen(engine).items():
        print(f"  {etiqueta}: {cantidad}")


if __name__ == "__main__":
    main()
