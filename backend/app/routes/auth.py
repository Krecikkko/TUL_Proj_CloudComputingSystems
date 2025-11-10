from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_session
from app.models.user import User
from app.schemas.auth import RegisterIn, LoginIn
from app.schemas.user import UserOut
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.config import access_token_expires
from app.utils.auth_deps import get_current_user, require_roles
from app.schemas.me import MeOut

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/register")
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_session)):
    # Check username/email uniqueness
    res = await db.execute(
        select(User).where((User.username == payload.username) | (User.email == payload.email))
    )
    existing = res.scalars().first()
    if existing:
        if existing.username == payload.username:
            raise HTTPException(status_code=400, detail="Username already taken")
        if existing.email == payload.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    return {"message": "User created successfully"}

@router.post("/login")
async def login(payload: LoginIn, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        subject={"id": user.id, "username": user.username},
        expires_delta=access_token_expires(),
    )
    return {"token": token, "user": UserOut.model_validate(user).model_dump()}

@router.get("/me", response_model=MeOut, summary="Get current user info from JWT")
async def get_me(user: User = Depends(get_current_user)):
    # user.role to Enum → serialising to string
    return MeOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=getattr(user.role, "name", str(user.role)),
    )

@router.post("/logout", status_code=204, summary="Logical logout (client removes token)")
async def logout(_: User = Depends(get_current_user)):
    # Lack of blacklist on the server's side — logging out means deletion of the token on the clients side
    return

