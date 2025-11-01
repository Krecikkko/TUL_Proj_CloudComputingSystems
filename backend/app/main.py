from fastapi import FastAPI
from app.routes import (
<<<<<<< HEAD
    users as users_router,
    auth as auth_router
=======
    files as files_router
>>>>>>> develop
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
<<<<<<< HEAD
app.include_router(users_router.router)
app.include_router(auth_router.router)
=======
app.include_router(files_router.router)
>>>>>>> develop

@app.get("/api")
def root():
    return {"message": "Hello from FastAPI!"}