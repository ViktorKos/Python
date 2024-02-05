import logging
from ipaddress import ip_address, ip_network
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.routes import auth, contacts_api, users
from src.config.config import config
from src.database.db import get_async_session


import re
from typing import Callable
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Black list
banned_ips = [
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"), ]


# ip_network("127.0.0.1")]


@app.middleware("http")
async def black_list(request: Request, call_next: Callable):
    client_ip = ip_address(request.client.host)

    for banned_ip in banned_ips:
        if client_ip in banned_ip:
            logger.error(f"IP address {client_ip} is banned")
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


user_agent_ban_list = [r"yandexbot", r"yandex-bot"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent", "")

    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent, re.IGNORECASE):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"}, )

    response = await call_next(request)
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(contacts_api.router, prefix="/api")
app.include_router(contacts_api.router_search, prefix='/api')
app.include_router(contacts_api.router_birthday, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def index():
    return {"message": "Contacts Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_async_session)):
    try:
        result = await db.execute(text(str("SELECT 1")))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to the database")
