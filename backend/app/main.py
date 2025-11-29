from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import (
    fileversion as fileversion_router,
    users as users_router,
    auth as auth_router,
    files as files_router,
    log as logbook_router,
    share as share_router,
    admin as admin_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach routers
app.include_router(users_router.router)
app.include_router(auth_router.router)
app.include_router(files_router.router)
app.include_router(fileversion_router.router)
app.include_router(logbook_router.router)
app.include_router(share_router.router)
app.include_router(admin_router.router)

@app.get("/api")
def root():
    return {"message": "Hello from FastAPI!"}