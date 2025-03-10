from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Source Models
class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    userId: str

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
