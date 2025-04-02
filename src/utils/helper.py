from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


docs_example = {
    "created_on": "2020-01-01T00:00:00.000001",
    "updated_on": "2020-01-01T00:00:00.000001"
}


class MetaDatetimeSchema(BaseModel):
    created_on: Optional[datetime]
    updated_on: Optional[datetime]

    class Config:
        from_attributes = True


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True, 
        from_attributes=True
    )


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")
