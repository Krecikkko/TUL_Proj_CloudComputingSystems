from fastapi import APIRouter, Depends, User

router = APIRouter(prefix="/api")

@router.post("/register")
def register():
    return {"hello": "rtegistrere"}