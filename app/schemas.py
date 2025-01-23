from pydantic import BaseModel, Field
from typing import Optional

class RunTestRequest(BaseModel):
    story_name: str = Field(..., description="Name of the story to test")
    at_api_base_url: str = Field(..., description="AskTable API base URL")
    at_api_key: str = Field(..., description="API key for authentication")
    model_group: Optional[str] = Field(None, description="LLM model group to use")
    case_name: Optional[str] = Field(None, description="Name of the case to run")
    force_recreate_db: bool = Field(False, description="Force to recreate the database")
    works: int = Field(2, description="Number of works to run")
    at_cloud_url: str = Field("https://cloud.asktable.com", description="AskTable Cloud URL")
    at_trace_url_prefix: str = Field("", description="Trace URL Prefix")
