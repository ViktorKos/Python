import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository.users import *


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = UserSchema(id=1, username='test_user', email="test_user@gmail.com", password="1Q2w3e4R",
                               confirmed=True)

    async def test_get_user_by_email_found(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_result

        result = await get_user_by_email(email="user@gmail.com", db=self.session)
        self.assertEqual(result, self.user)

    async def test_get_user_by_email_notfound(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result

        result = await get_user_by_email(email="nonexistent@gmail.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        new_user = User(**self.user.model_dump(), avatar=None)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = new_user
        self.session.execute.return_value = mocked_result
        result = await create_user(body=self.user, db=self.session)
        self.assertEqual(result.username, new_user.username)
        self.assertEqual(result.email, new_user.email)
        self.assertEqual(result.password, new_user.password)
        self.assertEqual(result.confirmed, new_user.confirmed)

    async def test_update_token(self):
        user = User(id=2, username='test_user', email='test_user@example.com', password='123QwErT', confirmed=True)
        token = "new_token"
        await update_token(user=user, token=token, db=self.session)
        self.assertEqual(user.refresh_token, token)

    async def test_confirmed_email(self):
        email = "test_user@gmail.com"
        mocked_user = User(**self.user.model_dump(), avatar=None)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = mocked_user
        self.session.execute.return_value = mocked_result
        await confirmed_email(email=email, db=self.session)
        self.assertTrue(mocked_user.confirmed)

    async def test_confirmed_email_notfound(self):
        email = "nonexistent@gmail.com"
        with self.assertRaises(ValueError):
            mocked_user = MagicMock()
            mocked_user.scalar_one_or_none.return_value = None
            self.session.execute.return_value = mocked_user
            await confirmed_email(email=email, db=self.session)

