from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from importlib import import_module
from .models.user import Base

DATABASE_URL = "sqlite+aiosqlite:///./dev.db"  # dev!!!!; later replace with Postgres
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# def _import_models():
#     # Import every model module so their tables register with Base.metadata
#     for m in ("app.models.user"):
#         import_module(m)

async def init_db():
    from app.models import user as models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)