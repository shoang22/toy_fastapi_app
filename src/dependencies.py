import uuid
from fastapi import Depends
from typing import Annotated


async def get_task_id():
    return uuid.uuid4()


TaskIDDependency = Annotated[uuid.UUID, Depends(get_task_id, use_cache=False)]
