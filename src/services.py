from typing import Callable, TypeVar, ParamSpec
# from anyio import Semaphore, to_thread
from fastapi.concurrency import run_in_threadpool

from src.loggers import logger
from src.utils import RecursiveCharacterTextStreamer


# MAX_CONCURRENT_THREADS = 1
# MAX_THREADS_GUARD = Semaphore(MAX_CONCURRENT_THREADS)

# T = TypeVar("T")
# P = ParamSpec("P")


# async def run_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
#     async with MAX_THREADS_GUARD:
#         return await run_in_threadpool(func, *args, **kwargs)


# @profile
async def nonblocking_call(text: str, task_id):
    # to_thread.current_default_thread_limiter().total_tokens = 1
    splitter = RecursiveCharacterTextStreamer()
    # text_chunks = await run_async(splitter.split_text, text=text) 
    text_chunks = await run_in_threadpool(splitter.split_text_stream, text=text)
    
    n_chunks = 0
    for _ in text_chunks:
        n_chunks += 1

    logger.info(f"Task {task_id} completed - N chunks: {n_chunks}")
