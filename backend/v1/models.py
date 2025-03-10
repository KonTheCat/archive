from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Background Task Models
class BackgroundTask(BaseModel):
    id: str
    taskType: str  # e.g., "text_extraction"
    status: str  # "pending", "in_progress", "completed", "failed", "cancelled"
    sourceId: Optional[str] = None
    pageId: Optional[str] = None
    scheduledAt: str  # When the task was created
    canCancel: bool  # Whether this task type can be cancelled

class BackgroundTaskResponse(BaseModel):
    data: BackgroundTask
    success: bool = True
    message: Optional[str] = None

class BackgroundTasksResponse(BaseModel):
    data: List[BackgroundTask]
    success: bool = True
    message: Optional[str] = None

# Source Models
class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    userId: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: str
    createdAt: str
    updatedAt: str

# Page Models
class PageBase(BaseModel):
    sourceId: str
    imageUrl: str
    extractedText: str
    title: Optional[str] = None
    date: Optional[str] = None
    notes: Optional[str] = None
    contentVector: Optional[List[float]] = None

class Page(PageBase):
    id: str
    createdAt: str
    updatedAt: str

# Response Models
class SourceResponse(BaseModel):
    data: Source
    success: bool = True
    message: Optional[str] = None

class SourcesResponse(BaseModel):
    data: List[Source]
    success: bool = True
    message: Optional[str] = None

class PageResponse(BaseModel):
    data: Page
    success: bool = True
    message: Optional[str] = None

class PagesResponse(BaseModel):
    data: List[Page]
    success: bool = True
    message: Optional[str] = None

class SearchResponse(BaseModel):
    data: Dict[str, List[Any]]
    success: bool = True
    message: Optional[str] = None
