from typing import TypeVar, Callable
from typing_extensions import ParamSpec

# Third party
from anyio import Semaphore
from fastapi.concurrency import run_in_threadpool

from src.utils import RecursiveCharacterTextStreamer

from src.broker import broker
from src.dependencies import RedisTaskiqDep


# To not have too many threads running (which could happen on too many concurrent
# requests, we limit it with a semaphore.
MAX_CONCURRENT_THREADS = 10
MAX_THREADS_GUARD = Semaphore(MAX_CONCURRENT_THREADS)
T = TypeVar("T")
P = ParamSpec("P")


async def run_async(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    async with MAX_THREADS_GUARD:
        return await run_in_threadpool(func, *args, **kwargs)


# Can we do dependency injection on broker tasks?
@broker.task(task_name="blocker")
async def nonblocking_call(text: str, task_id: str, db: RedisTaskiqDep):
    splitter = RecursiveCharacterTextStreamer()
    text_chunks = await run_async(splitter.split_text, text=text)

    n_chunks = 0
    for _ in text_chunks:
        n_chunks += 1

    # await db.setex(task_id, 600, n_chunks)
    await db.setex(task_id, 600, n_chunks)


@broker.task
async def my_redis_task(key: str, value: str, db: RedisTaskiqDep):
    await db.setex(key, 1, value)
    data = await db.get(key)
    print(f"task completed with {data}")
