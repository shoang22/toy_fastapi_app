import uuid
from fastapi import APIRouter, UploadFile, File, Depends, Query

from src.services import my_redis_task, nonblocking_call
from src.models import (
    UploadFileParamsRequest,
    UploadFileParamsResponse,
    MyVal,
    BaseResponse,
    BlockRequestBody,
)
from src.dependencies import TaskIDDep, RedisDep
from src.broker import broker
from src.loggers import logger

router = APIRouter()


@router.post("/block", response_model=BaseResponse)
async def get_blocked(
    file: UploadFile = File(...),
):
    task_id = str(uuid.uuid4())
    await broker.startup()
    logger.info(f"Task {task_id} initiated")
    text = (await file.read()).decode()

    data = BlockRequestBody(text=text, task_id=task_id)
    # await nonblocking_call.kicker().with_task_id(task_id).kiq(**data.model_dump())
    await nonblocking_call.kiq(**data.model_dump())

    return BaseResponse(response_id=task_id)


@router.post("/", response_model=UploadFileParamsResponse)
async def upload_file_json(
    task_id: TaskIDDep,
    params: UploadFileParamsRequest = Depends(),
    file: UploadFile = File(...),
):
    fixed_dict = {"properties": {"yo": "it's cool"}}
    fixed_dict["properties"].update(params.custom_fields)

    file = await file.read()
    return UploadFileParamsResponse(
        some_numbers=params.some_numbers,
        chunk_size=params.chunk_size,
        task_id=task_id,
        **params.custom_fields,
    )


@router.post("/insert")
async def insert_redis(body: MyVal):
    await my_redis_task.kiq(**body.model_dump())


@router.get("/get")
async def get_data(db: RedisDep, task_id: str = Query(...)):
    data = await db.get(task_id)
    return {"data": data}
