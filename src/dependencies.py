import redis.asyncio as redis
import uuid
from fastapi import Depends, Request
from taskiq import TaskiqDepends
from typing import Annotated


async def get_task_id() -> str:
    return str(uuid.uuid4())


TaskIDDep = Annotated[str, Depends(get_task_id, use_cache=False)]


def get_redis_taskiq(request: Request = TaskiqDepends()) -> redis.Redis:
    return request.app.state.redis


RedisTaskiqDep = Annotated[redis.Redis, TaskiqDepends(get_redis_taskiq)]


def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis


RedisDep = Annotated[redis.Redis, Depends(get_redis)]
