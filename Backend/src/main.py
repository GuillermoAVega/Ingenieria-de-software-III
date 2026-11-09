import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.database import (
    engine,
    migrar_detalle_reserva_legacy,
    migrar_estado_reserva_legacy,
)
from src.models import ModeloBase
from src.cliente.routers import router as clientes_router
from src.mesa.routers import router as mesas_router
from src.reserva.routers import router as reservas_router

# importamos los modelos para que registren sus tablas antes del create_all
from src.mozo import models as mozo_models
from src.sector import models as sector_models
from src.atencion import models as atencion_models

# importamos los routers desde nuestros modulos
from src.mozo.router import router as mozo_router
from src.sector.router import router as sector_router
from src.atencion.router import router as atencion_router
from src.routers import (
    comandas,
    comprobantes_pago,
    detalles_comanda,
    detalles_factura,
    facturas,
    medios_pago,
)
from fastapi.middleware.cors import CORSMiddleware
from src.productos import registro  # noqa: F401  (carga los mappers antes de create_all)
from src.productos.router import MANEJADORES_EXCEPCIONES as MANEJADORES_PRODUCTOS
from src.productos.router import router as router_productos
from src.promociones import models as promociones_models  # noqa: F401
from src.promociones.router import MANEJADORES_EXCEPCIONES as MANEJADORES_PROMOCIONES
from src.promociones.router import router as router_promociones
from src.productos_menu.router import MANEJADORES_EXCEPCIONES as MANEJADORES_PRODUCTOS_MENU
from src.productos_menu.router import router as router_productos_menu
from src.secciones.router import MANEJADORES_EXCEPCIONES as MANEJADORES_SECCIONES
from src.secciones.router import router as router_secciones
from src.reportes.router import router as router_reportes

load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH = os.getenv(f"ROOT_PATH_{ENV.upper()}")


@asynccontextmanager
async def db_creation_lifespan(app: FastAPI):
    ModeloBase.metadata.create_all(bind=engine)
    migrar_detalle_reserva_legacy()
    migrar_estado_reserva_legacy()
    yield


app = FastAPI(root_path=ROOT_PATH, lifespan=db_creation_lifespan)

origins = [
    "http://localhost:5173",  # para recibir requests desde app React (puerto: 5173)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# asociamos los routers a nuestra app
app.include_router(mozo_router)
app.include_router(sector_router)
app.include_router(atencion_router)
app.include_router(clientes_router)
app.include_router(mesas_router)
app.include_router(reservas_router)
app.include_router(router_productos)
app.include_router(router_secciones)
app.include_router(router_productos_menu)
app.include_router(router_promociones)
app.include_router(router_reportes)
app.include_router(medios_pago.router)
app.include_router(comandas.router)
app.include_router(detalles_comanda.router)
app.include_router(facturas.router)
app.include_router(detalles_factura.router)
app.include_router(comprobantes_pago.router)

for manejadores in (
    MANEJADORES_PRODUCTOS,
    MANEJADORES_SECCIONES,
    MANEJADORES_PRODUCTOS_MENU,
    MANEJADORES_PROMOCIONES,
):
    for tipo_excepcion, manejador in manejadores.items():
        app.add_exception_handler(tipo_excepcion, manejador)


