import asyncio

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from unittest.mock import MagicMock
from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.entity.models import Base, User, Contact
from src.database.db import get_async_session
from src.services.auth import auth_service
from src.config import messages

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

test_user = {"username": "deadpool", "email": messages.TEST_EMAIL, "password": "12345678"}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_user["password"])
            current_user = User(username=test_user["username"], email=test_user["email"], password=hash_password,
                                confirmed=True, role="admin", avatar="127.0.0.1://my_avatar.jpg")
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_async_session] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    access_token = await auth_service.create_access_token(data={"sub": test_user["email"], "DB-class": "PSQL"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": test_user["email"]})
    return access_token, refresh_token


@pytest.fixture
def app_without_limiter():
    app = FastAPI()

    @app.on_event("startup")
    async def startup_event():
        pass

    return app
