
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# Data received from the citizen
class ComplaintCreate(BaseModel):

    description: str = Field(min_length=5, max_length=2000)

    category: str | None = None

    location: str = Field(min_length=2, max_length=200)


# Data returned by the API
class ComplaintResponse(BaseModel):

    id: int
    description: str
    category: str | None
    location: str
    status: str
    created_at: datetime
    department: str | None = None

    model_config = ConfigDict(from_attributes=True)
class ComplaintStatusUpdate(BaseModel):
    status: str
class ComplaintDepartmentUpdate(BaseModel):
    department: str