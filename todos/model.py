from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form


class Todo(BaseModel):
    id: Optional[int] = None
    item: str

    @classmethod
    def as_form(cls, item: str = Form(...)):
        return cls(item=item)

    class Config:
        json_schema_extra = {
            "example": {
                "item": "Read the next chapter of the book, whose author is Marsel Timerbulatov!"
            }
        }


class TodoItem(BaseModel):
    item: str

    class Config:
        json_schema_extra = {
            "example": {
                "item": "Read the next chapter of the book"
            }
        }


class TodoItems(BaseModel):
    todos: List[Todo]

    class Config:
        json_schema_extra = {
            "example": {
                "todos": [
                    {
                        "id": 1,
                        "item": "Example schema 1!"
                    },
                    {
                        "id": 2,
                        "item": "Example schema 2!"
                    }
                ]
            }
        }
