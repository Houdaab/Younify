from typing import Optional, Literal

from pydantic import BaseModel, Field


class AddNodeRequest(BaseModel):
    state_data: str = Field(..., description="New brain state data")