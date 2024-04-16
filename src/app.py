from fastapi import FastAPI

from src.routes import router
from.services import lifespan


app = FastAPI(lifespan=lifespan)
app.include_router(router)

