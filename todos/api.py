from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from todo import todo_router

app = FastAPI()
templates = Jinja2Templates(directory="templates/")

@app.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request
    })

app.include_router(todo_router)
