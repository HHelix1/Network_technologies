from fastapi import APIRouter, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from models.users import User, UserSignIn

user_router = APIRouter(
    tags=["User"],
)

client = MongoClient('mongodb://localhost:27017/')
db = client['planner']
users_collection = db['users']

@user_router.post("/signup")
async def sign_user_up(user: User) -> dict:
    user_exist = users_collection.find_one({"email": user.email})
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email provided exists already."
        )
    users_collection.insert_one(user.dict())
    return {
        "message": "User created successfully"
    }

@user_router.post("/signin")
async def sign_user_in(user: UserSignIn) -> dict:
    user_exist = users_collection.find_one({"email": user.email})
    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with email does not exist."
        )
    if user_exist["password"] == user.password:
        return {
            "message": "User signed in successfully."
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )