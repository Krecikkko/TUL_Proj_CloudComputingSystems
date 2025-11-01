from fastapi import FastAPI
from app.routes import (
    files as files_router
)
from .db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    await init_db()
    yield
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

# Attach roouters
app.include_router(files_router.router)

@app.get("/api")
def root():
    return {"message": "Hello from FastAPI!"}