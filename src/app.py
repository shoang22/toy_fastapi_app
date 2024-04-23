from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_profiler import PyInstrumentProfilerMiddleware

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
