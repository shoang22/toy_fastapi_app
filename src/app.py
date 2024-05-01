import redis.asyncio as redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_profiler import PyInstrumentProfilerMiddleware

from src.routes import router
from src.broker import broker
from src.settings import settings


async def startup_taskiq() -> None:
    if not broker.is_worker_process:
        await broker.startup()


async def shutdown_taskiq() -> None:
    if not broker.is_worker_process:
        await broker.shutdown()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_taskiq()
    app.state.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
    yield
    await shutdown_taskiq()
    await app.state.redis.aclose()


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    if settings.PROFILE:
        app.add_middleware(
            PyInstrumentProfilerMiddleware,
            server_app=app,  # Required to output the profile on server shutdown
            profiler_output_type="html",
            is_print_each_request=True,  # Set to True to show request profile on
            # stdout on each request
            open_in_browser=False,  # Set to true to open your web-browser automatically
            # when the server shuts down
            html_file_name="example_profile.html",  # Filename for output
        )
    app.include_router(router)
    return app
