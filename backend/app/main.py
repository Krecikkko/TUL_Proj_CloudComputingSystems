from fastapi import FastAPI
from .routes import (
    fileversion as fileversion_router,
    users as users_router,
    auth as auth_router,
    files as files_router,
    log as logbook_router
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
app.include_router(users_router.router)
app.include_router(auth_router.router)
app.include_router(files_router.router)
app.include_router(fileversion_router.router)
app.include_router(logbook_router.router)

@app.get("/api")
def root():
    return {"message": "Hello from FastAPI!"}