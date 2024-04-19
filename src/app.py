from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.routes import router
from src.broker import broker


async def startup_taskiq() -> None:
    if not broker.is_worker_process:
        await broker.startup()


async def shutdown_taskiq() -> None:
    if not broker.is_worker_process:
        await broker.shutdown()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_taskiq()
    yield
    await shutdown_taskiq()


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)