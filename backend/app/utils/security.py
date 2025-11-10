from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.utils.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: dict, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    user_id = str(subject["id"])
    username = subject.get("username")
    to_encode = {
        "sub": user_id,
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
