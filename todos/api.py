from todo import todo_router 
from fastapi import FastAPI 
from todo import todo_router 
from model import Todo, TodoItem, TodoItems

app = FastAPI() 

@app.get("/") 
async def welcome() -> dict:return {"message": "Тимербулатов Марсель"}

async def retrieve_todo()->dict:
    return{
           "todos": todo_list
    }
@app.get("/todo")
async def retrieve_todo() -> dict:
    return {
        "todos": [
            {
                "id": 1,
                "item": "Example schema 1!"
            },
            {
                "id": 2,
                "item": "Example schema 2!"
            },
            {
                "id": 3,
                "item": "Example schema 5!"
            }
        ]
    }

app.include_router(todo_router)

