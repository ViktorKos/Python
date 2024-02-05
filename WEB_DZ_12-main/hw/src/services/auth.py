from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_async_session
from src.repository import users as rep_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "974790aec4ac460bdc11645decad4dce7c139b7f2982b7428ec44e886ea588c6"  # TODO: move to ENV file
    ALGORITHM = "HS256"
    ACCESS_TOKEN_MINUTES = 15
    REFRESH_TOKEN_DAYS = 7

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str):
        return cls.pwd_context.hash(password)

    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        expires_delta = expires_delta or timedelta(minutes=cls.ACCESS_TOKEN_MINUTES)
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    async def create_refresh_token(cls, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        expires_delta = expires_delta or timedelta(days=cls.REFRESH_TOKEN_DAYS)
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    async def decode_refresh_token(cls, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                return payload['sub']
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    @classmethod
    async def get_current_user(cls, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_session)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await rep_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user


auth_service = Auth()
