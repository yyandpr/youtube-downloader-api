from pydantic import BaseModel, HttpUrl
from typing import Optional

class DownloadRequest(BaseModel):
    url: str
    translate_subtitles: bool = False

class DownloadResponse(BaseModel):
    task_id: str
    status: str

class ProgressEvent(BaseModel):
    task_id: str
    stage: str  # downloading, extracting_subs, translating, merging, embedding, complete, error
    progress: float
    speed: Optional[str] = None
    eta: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    filename: Optional[str] = None
    error: Optional[str] = None
