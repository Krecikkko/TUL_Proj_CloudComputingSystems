from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from importlib import import_module
from .models.base import Base

DATABASE_URL = "sqlite+aiosqlite:///./dev.db"  # dev!!!!; later replace with Postgres
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    _import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def _import_models():
    for m in (
        ("app.models.user"),
        ("app.models.file")
    ):
        import_module(m)

async def init_db():
    _import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
