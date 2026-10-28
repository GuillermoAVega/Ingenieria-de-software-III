import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from src.database import engine, migrar_detalle_reserva_legacy
from src.models import ModeloBase
from src.cliente.routers import router as clientes_router
from src.mesa.routers import router as mesas_router
from src.reserva.routers import router as reservas_router

# importamos los routers desde nuestros modulos
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

ENV = os.getenv("ENV")
ROOT_PATH = os.getenv(f"ROOT_PATH_{ENV.upper()}")


@asynccontextmanager
async def db_creation_lifespan(app: FastAPI):
    ModeloBase.metadata.create_all(bind=engine)
    migrar_detalle_reserva_legacy()
    yield


app = FastAPI(root_path=ROOT_PATH, lifespan=db_creation_lifespan)
app.include_router(clientes_router)
app.include_router(mesas_router)
app.include_router(reservas_router)

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
