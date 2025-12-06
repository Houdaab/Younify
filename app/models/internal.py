from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class BrainStateNodeModel(BaseModel):
    state_data: str = Field(..., description="Comma-separated string of brain state values")
    previous_hash: str = Field(..., description="Hash of the previous node")
    hash: str = Field(..., description="SHA-256 hash of this node")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")


class UpdateChainRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]] = None
