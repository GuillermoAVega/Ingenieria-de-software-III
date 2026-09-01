from fastapi import FastAPI

from app.backend import database
from app.backend.routes.clientes import router as clientes_router
from app.backend.routes.productos import router as productos_router
from app.backend.routes.ventas import router as ventas_router

database.create_tables()

app = FastAPI(title="Propuesta de Productividad — API")
app.include_router(clientes_router)
app.include_router(productos_router)
app.include_router(ventas_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
