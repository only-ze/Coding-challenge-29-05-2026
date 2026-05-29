from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.db import Base, engine, get_db
from app.routers.clients import router as clientes_router
from app.routers.webhooks import router as webhooks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Mundo Invest — Client Management API",
    description=(
        "API interna para gestão de clientes e seus patrimônios investidos, "
        "com integração simulada ao Pipefy via GraphQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(clientes_router)
app.include_router(webhooks_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}