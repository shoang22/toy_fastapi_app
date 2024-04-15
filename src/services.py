import concurrent.futures
import time
import asyncio
import concurrent
from functools import partial
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

from src.loggers import logger
from src.utils import RecursiveCharacterTextStreamer


def heavy_computation_try_catch():
    try:
        time.sleep(10)
    except Exception as e:
        # This is not being caught...error is not making it to the app-level
        with open("logs/blocking_error.txt", "w") as f:
            f.write(f"[ERROR] {str(e)}")


def heavy_computation_sync():
    time.sleep(10)


async def heavy_computation_async(task_id):
    await asyncio.sleep(10)
    logger.info(f"Task {task_id} completed")


async def blocking_call(text: str, task_id):
    # Since time.sleep is a blocking call,
    # This will prevent FastAPI from executing the BackgroundTask first
    # So we run it in another thread with run_in_threadpool
    await run_in_threadpool(heavy_computation_sync)
    splitter = RecursiveCharacterTextSplitter()
    text_chunks = splitter.split_text(text=text)
    logger.info(f"Task {task_id} completed. N_chunks: {len(text_chunks)}")


async def nonblocking_call(text: str, task_id):
    splitter = RecursiveCharacterTextStreamer()
    text_chunks = await run_in_threadpool(splitter.split_text, text=text)

    # loop = asyncio.get_running_loop()
    # text_chunks = await loop.run_in_executor(None, partial(splitter.split_text, text=text))
    # await loop.run_in_executor(None, heavy_computation_sync)
    # with concurrent.futures.ThreadPoolExecutor() as pool:
    #     text_chunks = await loop.run_in_executor(pool, partial(splitter.split_text, text=text))

    n_chunks = 0
    for _ in text_chunks:
        n_chunks += 1

    logger.info(f"Task {task_id} completed - N chunks: {n_chunks}")
