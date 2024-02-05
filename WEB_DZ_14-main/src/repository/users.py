from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_async_session
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_async_session)):
    """
   The get_user_by_email function returns a user object from the database based on the email address provided.
       If no user is found, None is returned.

   :param email: str: Get the email of a user
   :param db: AsyncSession: Pass the database session into the function
   :return: A user object
   :doc-author: Trelent
   """

    statement = select(User).filter_by(email=email)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_async_session)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body and convert it to a userschema object
    :param db: AsyncSession: Pass the database session to the function
    :return: The new user object
    :doc-author: Trelent
    """

    avatar = None
    try:
        gr_avatar = Gravatar(body.email)
        avatar = gr_avatar.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the user's refresh token in the database.

    :param user: User: Identify the user that is being updated
    :param token: str | None: Update the user's refresh token
    :param db: AsyncSession: Make sure that the database session is closed after the function has been executed
    :return: None, so the return value of this function is none
    :doc-author: Trelent
    """

    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function marks a user as confirmed in the database.

    :param email: str: Get the email of the user
    :param db: AsyncSession: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """

    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Get the user from the database
    :param url: str | None: Specify that the url parameter can be either a string or none
    :param db: AsyncSession: Pass in the database session
    :return: The updated user object
    :doc-author: Trelent
    """

    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
