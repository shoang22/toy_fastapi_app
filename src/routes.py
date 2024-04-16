from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Request

from src.services import nonblocking_call, Item
from src.responses import BaseResponse
from src.dependencies import TaskIDDependency 
from src.loggers import logger

router = APIRouter()

@router.post("/block", response_model=BaseResponse)
async def get_blocked(
    background_task: BackgroundTasks, 
    task_id: TaskIDDependency, 
    file: UploadFile = File(...),
):
    logger.info(f"Task {task_id} initiated")
    text = (await file.read()).decode()

    background_task.add_task(
        nonblocking_call, 
        text=text,
        task_id=task_id, 
    )

    return BaseResponse(response_id=task_id)


@router.post("/add", response_model=BaseResponse)
async def add_task(
    request: Request,
    task_id: TaskIDDependency, 
    file: UploadFile = File(...),
):
    text = (await file.read()).decode()

    item = Item(task_id=task_id, text=text)
    request.state.q.put_nowait(item)
    logger.info(f"Task {task_id} initiated")
    return BaseResponse(response_id=task_id)