from fastapi import FastAPI
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
import redis.asyncio as redis 
from fastapi_limiter import FastAPILimiter 
import os 


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    await init_db()
    
    # === Rate Limiting Initialization ===
    print(f"Initializing Rate Limiter with Redis at {REDIS_URL}...")
    try:
        redis_connection = redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
        await FastAPILimiter.init(redis_connection)
    except Exception as e:
        print(f"INITIALIZATION ERROR REDIS/FASTAPILIMITER: {e}")
        
    yield
    # === Rate Limiter Cleanup ===
    try:
        await FastAPILimiter.close() 
    except Exception:
        pass 
        
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

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