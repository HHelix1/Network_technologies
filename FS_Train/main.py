from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine, Base, SessionLocal
from routes import router

def create_tables():
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Таблицы базы данных созданы!")
    yield
    print("Приложение останавливается...")

app = FastAPI(
    title="Система учета обучения сотрудников",
    description="Микросервисная система для управления обучением сотрудников",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в систему учета обучения сотрудников!",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "educational_programs": "/educational-programs/",
            "employees": "/employees/",
            "training": "/training-assignments/",
            "auth": "/auth/",
            "users": "/users/"
        }
    }



if __name__ == "__main__":
    import uvicorn
    print("Документация: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

