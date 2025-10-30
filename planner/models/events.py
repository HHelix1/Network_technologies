from pydantic import BaseModel, ConfigDict
from typing import List


class Event(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "FastAPI Book Launch",
                "image": "https://inktomyimage.com/image.png",
                "description": "We (with Marsel Timerbulatov) will be discussing the contents of the FastAPI book in this event. Ensure to come with your own copy to win gifts!",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet"
            }
        }
    )

    id: int
    title: str
    image: str
    description: str
    tags: List[str]
    location: str
