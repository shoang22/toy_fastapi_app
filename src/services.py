from fastapi.concurrency import run_in_threadpool
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.broker import broker
from src.dependencies import RedisTaskiqDep


# Can we do dependency injection on broker tasks?
@broker.task(task_name="blocker")
async def nonblocking_call(text: str, task_id: str, db: RedisTaskiqDep):
    splitter = RecursiveCharacterTextSplitter()
    text_chunks = await run_in_threadpool(splitter.split_text, text=text)

    n_chunks = 0
    for _ in text_chunks:
        n_chunks += 1

    await db.setex(task_id, 600, n_chunks)
    print(n_chunks)


@broker.task
async def my_redis_task(key: str, value: str, db: RedisTaskiqDep):
    await db.setex(key, 1, value)
    data = await db.get(key)
    print(f"task completed with {data}")


# TODO: Review natsbroker source code
