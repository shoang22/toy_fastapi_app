import uuid
import asyncio
from contextlib import asynccontextmanager  
from fastapi import FastAPI
from functools import partial
from fastapi.concurrency import run_in_threadpool
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from concurrent.futures import ProcessPoolExecutor
from pydantic import BaseModel, Field

from src.loggers import logger


class Item(BaseModel):
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    text: str


async def process_requests(q: asyncio.Queue, pool: ProcessPoolExecutor):
    while True:
        item = await q.get()
        loop = asyncio.get_running_loop()
        splitter = RecursiveCharacterTextSplitter()
        text_chunks = await loop.run_in_executor(pool, partial(splitter.split_text, text=item.text))
        q.task_done()         

        n_chunks = 0
        for _ in text_chunks:
            n_chunks += 1

        logger.info(f"Task {item.task_id} completed - N chunks: {n_chunks}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    q = asyncio.Queue()
    pool = ProcessPoolExecutor()
    asyncio.create_task(process_requests(q, pool))
    yield {"q": q, "pool": pool}
    pool.shutdown()


async def nonblocking_call(text: str, task_id):
    loop = asyncio.get_running_loop()
    splitter = RecursiveCharacterTextSplitter()

    with ProcessPoolExecutor() as pool:
        text_chunks = await loop.run_in_executor(pool, partial(splitter.split_text, text=text))
   
    text_chunks = await run_in_threadpool(splitter.split_text, text=text)
    
    n_chunks = 0
    for _ in text_chunks:
        n_chunks += 1

    logger.info(f"Task {task_id} completed - N chunks: {n_chunks}")
