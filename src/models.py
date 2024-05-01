import json
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
from typing import Optional
from fastapi import Query


class BaseResponse(BaseModel):
    response_id: str


class BlockRequestBody(BaseModel):
    text: str
    task_id: str


class CreateFileRequest(BaseModel):
    chunk_size: Optional[int] = Field(default=None)
    custom_fields: str = Field(default="{}")

    @field_validator("custom_fields")
    @classmethod
    def validate_to_json(cls, value):
        return json.loads(value)


class UploadFileParamsRequest(BaseModel):
    chunk_size: Optional[int] = Field(default=None)
    some_numbers: list[int] = Field(Query(default=[1, 2, 3]))
    custom_fields: str = Field(default="{}")

    @field_validator("custom_fields")
    @classmethod
    def validate_to_json(cls, value):
        return json.loads(value)


class UploadFileParamsResponse(BaseResponse):
    model_config = ConfigDict(extra="allow")

    some_numbers: list[int] = Field(default_factory=list)


class MyVal(BaseModel):
    key: str
    value: str
