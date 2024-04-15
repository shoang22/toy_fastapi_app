import uuid
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    response_id: uuid.UUID = Field(default_factory=uuid.uuid4)