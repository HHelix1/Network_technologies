from fastapi import FastAPI
from routes.events import event_router
from routes.users import user_router

app = FastAPI()

app.include_router(event_router, prefix="/event")
app.include_router(user_router, prefix="/user")

@app.get("/")
async def root():
    return {"message": "FastAPI Server is running!"}