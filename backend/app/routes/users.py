from fastapi import APIRouter, Depends
from ..models.user import User

router = APIRouter(prefix="/api")

# @router.post("/register")
# def register():
#     return {"hello": "rtegistrere"}