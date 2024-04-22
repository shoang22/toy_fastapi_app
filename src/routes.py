from fastapi import APIRouter, BackgroundTasks, UploadFile, File

from src.services import nonblocking_call
from src.responses import BaseResponse
from src.dependencies import TaskIDDependency
from src.loggers import logger
from src.broker import broker

router = APIRouter()


@router.post("/block", response_model=BaseResponse)
async def get_blocked(
    task_id: TaskIDDependency,
    file: UploadFile = File(...),
):
    await broker.startup()
    logger.info(f"Task {task_id} initiated")
    text = (await file.read()).decode()
    task = await nonblocking_call.kiq(text=text, task_id=task_id)
    result = await task.wait_result()

    return BaseResponse(response_id=task_id)
