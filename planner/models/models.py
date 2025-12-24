from pydantic import BaseModel
from typing import List, Optional

class Event(BaseModel):
    title: str
    image: str
    description: str
    tags: List[str]
    location: str

class EventUpdate(BaseModel):
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
