import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.database import engine
from src.models import ModeloBase

# importamos los routers desde nuestros modulos
from fastapi.middleware.cors import CORSMiddleware
from src.productos import registro  # noqa: F401  (carga los mappers antes de create_all)
from src.productos.router import MANEJADORES_EXCEPCIONES as MANEJADORES_PRODUCTOS
from src.productos.router import router as router_productos
from src.productos_menu.router import MANEJADORES_EXCEPCIONES as MANEJADORES_PRODUCTOS_MENU
from src.productos_menu.router import router as router_productos_menu
from src.secciones.router import MANEJADORES_EXCEPCIONES as MANEJADORES_SECCIONES
from src.secciones.router import router as router_secciones

load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH = os.getenv(f"ROOT_PATH_{ENV.upper()}")


@asynccontextmanager
async def db_creation_lifespan(app: FastAPI):
    ModeloBase.metadata.create_all(bind=engine)
    yield


app = FastAPI(root_path=ROOT_PATH, lifespan=db_creation_lifespan)

origins = [
    "http://localhost:5173", # para recibir requests desde app React (puerto: 5173)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_productos)
app.include_router(router_secciones)
app.include_router(router_productos_menu)

for manejadores in (
    MANEJADORES_PRODUCTOS,
    MANEJADORES_SECCIONES,
    MANEJADORES_PRODUCTOS_MENU,
):
    for tipo_excepcion, manejador in manejadores.items():
        app.add_exception_handler(tipo_excepcion, manejador)
