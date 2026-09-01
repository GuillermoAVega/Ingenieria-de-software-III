from fastapi import FastAPI

from app.backend import database
from app.backend.routes.clientes import router

database.create_tables()

app = FastAPI(title="Propuesta de Productividad — API")
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
