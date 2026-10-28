import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.database import engine
from src.models import ModeloBase

# importamos los routers desde nuestros modulos
from fastapi.middleware.cors import CORSMiddleware
from src.productos import registro  # noqa: F401  (carga los mappers antes de create_all)
from src.productos.router import MANEJADORES_EXCEPCIONES
from src.productos.router import router as router_productos

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

for tipo_excepcion, manejador in MANEJADORES_EXCEPCIONES.items():
    app.add_exception_handler(tipo_excepcion, manejador)
