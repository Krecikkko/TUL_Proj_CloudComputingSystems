from fastapi import FastAPI
from app.routes import (
    users as users_router
)

app = FastAPI()

# Attach routers
app.include_router(users_router.router)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI!"}