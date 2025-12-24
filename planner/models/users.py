from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from models.events import Event


class User(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!",
                "events": []
            }
        }
    )

    email: EmailStr
    password: str
    events: Optional[List[Event]] = []


class NewUser(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!",
                "username": "FastPackt"
            }
        }
    )

    email: EmailStr
    password: str
    username: str


class UserSignIn(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!"
            }
        }
    )

    email: EmailStr
    password: str
