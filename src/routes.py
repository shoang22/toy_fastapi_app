from fastapi import APIRouter, UploadFile, File, Depends

from src.services import nonblocking_call
from src.models import (
    BaseResponse,
    UploadFileParamsRequest,
    UploadFileParamsResponse,
    CreateFileRequest,
)
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


@router.post("/", response_model=UploadFileParamsResponse)
async def upload_file_json(
    task_id: TaskIDDependency,
    params: UploadFileParamsRequest = Depends(),
    file: UploadFile = File(...),
):
    fixed_dict = {"properties": {"yo": "it's cool"}}
    fixed_dict["properties"].update(params.custom_fields)

    file = await file.read()
    return UploadFileParamsResponse(
        some_numbers=params.some_numbers,
        task_id=task_id,
        **params.custom_fields,
    )


@router.post("/create", response_model=UploadFileParamsResponse)
async def upload_file_json(
    params: CreateFileRequest,
):
    return {"processed_as": type(params.custom_fields)}
