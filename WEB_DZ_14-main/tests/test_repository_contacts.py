import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import Date, func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact_schemas import ContactSchema, ContactUpdateSchema
from src.repository.contacts import *


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', email="user@gmail.com", password="123qwerty", confirmed=True)
        self.contact = ContactSchema(first_name="John", last_name="Doe", email="john.doe@example.com",
                                     phone_number="1234567890", birth_date="1990-01-01", crm_status="operational")

    async def test_get_contacts(self):
        contacts = [Contact(id=1, first_name="John", last_name="Biden", email="john.biden@whitehouse.gov",
                            phone_number="0115550011", birth_date="09.09.1947", crm_status="corporative"),
                    Contact(id=2, first_name="John", last_name="Secada", email="john.secada@yahoo.com",
                            phone_number="0115558800", birth_date="02.02.1966", crm_status="operational"),
                    Contact(id=3, first_name="Lesley", last_name="Nilsen", email="lesley-joke@ontario.cd",
                            phone_number="0135550055", birth_date="02.02.1950", crm_status="analitic")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit=10, offset=0, db=self.session, user=self.user)
        self.assertEqual(result, contacts)

    async def test_get_contacts_notfound(self):
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = list()
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit=10, offset=0, db=self.session, user=self.user)
        self.assertEqual(result, list())

    async def test_get_contacts_all(self):
        contacts = [Contact(id=1, first_name="John", last_name="Biden", email="john.biden@whitehouse.gov",
                            phone_number="0115550011", birth_date="09.09.1947", crm_status="corporative"),
                    Contact(id=2, first_name="John", last_name="Secada", email="john.secada@yahoo.com",
                            phone_number="0115558800", birth_date="02.02.1966", crm_status="operational"),
                    Contact(id=3, first_name="Lesley", last_name="Nilsen", email="lesley-joke@ontario.cd",
                            phone_number="0135550055", birth_date="02.02.1950", crm_status="analitic")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts_all(limit=10, offset=0, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact(id=1, first_name="John", last_name="Biden", email="john.biden@whitehouse.gov",
                          phone_number="0115550011", birth_date="09.09.1947", crm_status="corporative")
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(contact_id=1, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_get_contact_notfound(self):
        contact_id = 4
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(contact_id=contact_id, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_create_contact(self):
        new_data = ContactSchema(id=1, first_name="John", last_name="Doe", email="john.doe@example.com",
                                 phone_number="1234567890", birth_date="1990-01-01", crm_status="operational")
        new_contact = Contact(**new_data.model_dump(exclude_unset=True), user=self.user)
        result = await create_contact(body=self.contact, db=self.session, user=self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, new_contact.first_name)
        self.assertEqual(result.last_name, new_contact.last_name)
        self.assertEqual(result.email, new_contact.email)
        self.assertEqual(result.phone_number, new_contact.phone_number)
        self.assertEqual(result.birth_date, new_contact.birth_date)
        self.assertEqual(result.crm_status, new_contact.crm_status)

    async def test_update_contact(self):
        contact_id = 1
        mocked_contact = ContactSchema(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com",
                                       phone_number="1234567890", birth_date="1990-01-01", crm_status="operational")
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = Contact(id=contact_id, first_name="John", last_name="Doe",
                                                                  email="john.doe@example.com",
                                                                  phone_number="1234567890",
                                                                  birth_date="1990-01-01", crm_status="operational")
        self.session.execute.return_value = mocked_contacts
        result = await update_contact(contact_id=contact_id, body=self.contact, db=self.session, user=self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, self.contact.first_name)
        self.assertEqual(result.last_name, self.contact.last_name)
        self.assertEqual(result.email, self.contact.email)
        self.assertEqual(result.phone_number, self.contact.phone_number)
        self.assertEqual(result.birth_date, self.contact.birth_date)
        self.assertEqual(result.crm_status, self.contact.crm_status)

    async def test_update_contact_notfound(self):
        contact_id = 4
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_result
        result = await update_contact(contact_id=contact_id, body=self.contact, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_delete_contact(self):
        contact_id = 1
        mocked_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com",
                                 phone_number="1234567890", birth_date="1990.01.01", crm_status="operational")
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = mocked_contact
        self.session.execute.return_value = mocked_contacts
        result = await delete_contact(contact_id=contact_id, db=self.session, user=self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.id, contact_id)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

    async def test_delete_contact_notfound(self):
        contact_id = 4
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(contact_id=contact_id, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_search_contact_by_firstname(self):
        contact_id = 1
        mocked_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com",
                                 phone_number="1234567890", birth_date="1990.01.01", crm_status="operational")
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = mocked_contact
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_firstname(contact_first_name="John", db=self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, self.contact.first_name)
        self.assertEqual(result.last_name, self.contact.last_name)
        self.assertEqual(result.email, self.contact.email)
        self.assertEqual(result.phone_number, self.contact.phone_number)
        self.assertEqual(result.birth_date, datetime.strftime(self.contact.birth_date, '%Y.%m.%d'))
        self.assertEqual(result.crm_status, self.contact.crm_status)

    async def test_search_contact_by_firstname_notfound(self):
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = None
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_firstname(contact_first_name="Janet", db=self.session)
        self.assertIsNone(result)

    async def test_search_contact_by_lasttname(self):
        contact_id = 1
        mocked_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com",
                                 phone_number="1234567890", birth_date="1990.01.01", crm_status="operational")
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = mocked_contact
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_lastname(contact_last_name="Doe", db=self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, self.contact.first_name)
        self.assertEqual(result.last_name, self.contact.last_name)
        self.assertEqual(result.email, self.contact.email)
        self.assertEqual(result.phone_number, self.contact.phone_number)
        self.assertEqual(result.birth_date, datetime.strftime(self.contact.birth_date, '%Y.%m.%d'))
        self.assertEqual(result.crm_status, self.contact.crm_status)

    async def test_search_contact_by_lastname_notfound(self):
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = None
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_lastname(contact_last_name="Jackson", db=self.session)
        self.assertIsNone(result)

    async def test_search_contact_by_email(self):
        contact_id = 1
        mocked_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com",
                                 phone_number="1234567890", birth_date="1990.01.01", crm_status="operational")
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = mocked_contact
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_email(contact_email="doe", db=self.session)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, self.contact.first_name)
        self.assertEqual(result.last_name, self.contact.last_name)
        self.assertEqual(result.email, self.contact.email)
        self.assertEqual(result.phone_number, self.contact.phone_number)
        self.assertEqual(result.birth_date, datetime.strftime(self.contact.birth_date, '%Y.%m.%d'))
        self.assertEqual(result.crm_status, self.contact.crm_status)

    async def test_search_contact_by_email_notfound(self):
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = None
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_email(contact_email="jack", db=self.session)
        self.assertIsNone(result)

    async def test_search_contact_query(self):
        contacts = [Contact(id=1, first_name="John", last_name="Biden", email="john.biden@whitehouse.gov",
                            phone_number="0115550011", birth_date="09.09.1947", crm_status="corporative"),
                    Contact(id=2, first_name="John", last_name="Secada", email="mr.secada@yahoo.com",
                            phone_number="0115558800", birth_date="02.02.1966", crm_status="operational"),
                    Contact(id=3, first_name="Lesley", last_name="Nilsen", email="lesley-joke@johnwille.cd",
                            phone_number="0135550055", birth_date="03.03.1950", crm_status="analitic")]
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_result
        result = await search_contact_query(query="John", db=self.session)
        self.assertEqual(result, contacts)
        self.assertEqual(len(result), len(contacts))

    async def test_search_contact_query_notfound(self):
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = None
        self.session.execute.return_value = mocked_result
        result = await search_contact_query(query="Janet", db=self.session)
        self.assertIsNone(result)

    async def test_search_contact_by_birthdate(self):
        contacts = [Contact(id=2, first_name="John", last_name="Secada", email="mr.secada@yahoo.com",
                            phone_number="0115558800", birth_date="02.02.1966", crm_status="operational"),
                    Contact(id=3, first_name="Lesley", last_name="Nilsen", email="lesley-joke@johnwille.cd",
                            phone_number="0135550055", birth_date="03.03.1950", crm_status="analitic")]
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_result
        result = await search_contact_by_birthdate(forward_shift_days=100, db=self.session)
        self.assertEqual(result, contacts)
        self.assertEqual(len(result), len(contacts))


