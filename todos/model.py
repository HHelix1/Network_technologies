
from pydantic import BaseModel

class Item(BaseModel):
    item: str
    status: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "item": {
                    "item": "Example task",
                    "status": "completed"
                },
                "id": 2,
                "item": {
                    "item": "Marsel",
                    "status": "busy"

            }
        }
    }


class Todo(BaseModel):
    id: int
    item: Item
