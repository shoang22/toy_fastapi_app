import copy
from fastapi import APIRouter, BackgroundTasks, UploadFile, Query, File

from src.services import blocking_call, nonblocking_call, heavy_computation_async
from src.responses import BaseResponse
from src.dependencies import TaskIDDependency 
from src.loggers import logger
from src.utils import RecursiveCharacterTextStreamer

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