import json
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, Query
from typing import Dict, List

from src.services import nonblocking_call
from src.models import (
    BaseResponse,
    UploadFileParamsRequest,
    UploadFileParamsResponse,
    CreateFileRequest,
)
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


@router.post("/", response_model=UploadFileParamsResponse)
async def upload_file_json(
    task_id: TaskIDDependency,
    params: UploadFileParamsRequest = Depends(),
    file: UploadFile = File(...),
):
    print(f"Field is: {params.custom_fields} with type: {type(params.custom_fields)}")

    fixed_dict = {"properties": {"yo": "it's cool"}}
    fixed_dict["properties"].update(params.custom_fields)
    print(fixed_dict)

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
    print(f"Field is: {params.custom_fields} with type: {type(params.custom_fields)}")
    return {"haha": "hahahahhaha"}
