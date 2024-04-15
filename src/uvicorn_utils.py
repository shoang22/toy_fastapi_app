from uvicorn.workers import UvicornWorker

MyUvicornWorker = UvicornWorker
MyUvicornWorker.CONFIG_KWARGS = {"loop": "asyncio", "http": "auto"}