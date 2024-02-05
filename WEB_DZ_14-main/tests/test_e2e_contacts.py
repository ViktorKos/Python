from datetime import datetime, date
from unittest.mock import Mock, patch, AsyncMock

import json
import pytest
from requests.models import PreparedRequest
from sqlalchemy import select
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.entity.models import User, Contact
from tests.conftest import TestingSessionLocal, client, get_token, app_without_limiter
from src.config import messages
from src.schemas.contact_schemas import ContactSchema, ContactResponseSchema
from src.services.auth import auth_service
from src.repository import contacts as rep_contacts


def test_get_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token[0]}"})
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


def test_get_contacts_all(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/api/contacts/all", headers={"Authorization": f"Bearer {get_token[0]}"})
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


def test_get_contact_notfound(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/api/contacts/1", headers={"Authorization": f"Bearer {get_token[0]}"})
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == messages.ENTITY_NOT_FOUND


def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        current_contact = ContactSchema(first_name="Janet", last_name="Jackson", email="janet@jacksonwille.biz",
                                        phone_number="0135558822", birth_date=date(1968, 7, 27))

        contact_dict = current_contact.dict()
        contact_dict['birth_date'] = contact_dict['birth_date'].isoformat()

        response = client.post("/api/contacts/", headers={"Authorization": f"Bearer {get_token[0]}"},
                               json={**contact_dict, "user": "deadpool@example.com",
                                     "avatar": "127.0.0.1://my_avatar.jpg"}, )
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Janet"
        assert data["last_name"] == "Jackson"
        assert data["email"] == "janet@jacksonwille.biz"
        assert data["phone_number"] == "0135558822"
        assert data["birth_date"] == "1968-07-27"


@pytest.mark.asyncio
async def test_get_contact(client, get_token, monkeypatch):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == "deadpool@example.com"))
        current_user = current_user.scalar_one_or_none()
        test_contact1 = Contact(first_name="John", last_name="Bon Jovi", email="john.jovi@undergraund.tv",
                                phone_number="0115551212", birth_date=date(1961, 1, 31), crm_status="corporative",
                                user=current_user)
        session.add(test_contact1)
        await session.commit()
        await session.refresh(test_contact1)

    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get("/api/contacts/1", headers={"Authorization": f"Bearer {get_token[0]}"})
        # Assertions
        assert response.status_code == 200, response.text


def test_update_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        contact = ContactSchema(first_name="John", last_name="Bon Jovi", email="john.bon.jovi@glam-metal.by",
                                phone_number="0115559900", birth_date=date(1961, 1, 31))
        contact_dict = contact.dict()
        contact_dict['birth_date'] = contact_dict['birth_date'].isoformat()
        response = client.put("/api/contacts/1", headers={"Authorization": f"Bearer {get_token[0]}"},
                              json={**contact_dict})
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Bon Jovi"
        assert data["email"] == "john.bon.jovi@glam-metal.by"
        assert data["phone_number"] == "0115559900"
        assert data["birth_date"] == "1961-01-31"


def test_delete_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.delete("/api/contacts/1", headers={"Authorization": f"Bearer {get_token[0]}"})
        # Assertions
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_search_contact_by_birthdate(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        async with TestingSessionLocal() as session:
            current_user = await session.execute(select(User).where(User.email == "deadpool@example.com"))
            current_user = current_user.scalar_one_or_none()
            test_contact2 = Contact(first_name="Nana", last_name="Kwame", email="darkman@germany.eu",
                                    phone_number="0373335500", birth_date=date(1968, 10, 5), user=current_user)
            test_contact3 = Contact(first_name="Lenny", last_name="Wolf", email="wooooooohn@ahtung.de",
                                    phone_number="0314441200", birth_date=date(1962, 3, 11), crm_status="corporative",
                                    user=current_user)
            session.add(test_contact2)
            session.add(test_contact3)
            await session.commit()
            await session.refresh(test_contact2)
            await session.refresh(test_contact3)

        request_payload = 100
        response_payload = [ContactResponseSchema(**{"id": 2, "first_name": "John", "last_name": "Bon Jovi",
                                                     "email": "john.jovi@undergraund.tv", "phone_number": "0115551212",
                                                     "birth_date": date(1961, 1, 31), "crm_status": "corporative",
                                                     "created_at": None, "updated_at": None}),
                            ContactResponseSchema(**{"id": 4, "first_name": "Lenny", "last_name": "Wolf",
                                                     "email": "wooooooohn@ahtung.de", "phone_number": "0314441200",
                                                     "birth_date": date(1962, 3, 11), "crm_status": "corporative",
                                                     "created_at": None, "updated_at": None}), ]

        mock_search_contact_by_birthdate = AsyncMock(request_payload)
        monkeypatch.setattr("src.routes.birthday_contacts.search_contact_by_birthdate",
                            mock_search_contact_by_birthdate)

        response = client.get(f"/api/birthday/{request_payload}", headers={"Authorization": f"Bearer {get_token[0]}"})
        data = json.loads(response.text)

        assert response.status_code == 200
        assert len(data) == 2

        assert data[0]["first_name"] == response_payload[0].first_name
        assert data[0]["last_name"] == response_payload[0].last_name
        assert datetime.strptime(data[0]["birth_date"], "%Y-%m-%d").date() == response_payload[0].birth_date

        assert data[1]["first_name"] == response_payload[1].first_name
        assert data[1]["last_name"] == response_payload[1].last_name
        assert datetime.strptime(data[1]["birth_date"], "%Y-%m-%d").date() == response_payload[1].birth_date


@pytest.mark.asyncio
async def test_search_contact_by_firstname(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        async with TestingSessionLocal() as session:
            attrb = "ohn"
            queries = await rep_contacts.search_contact_by_firstname(attrb, session)

            response = client.get(f"/api/search/by_firstname/{attrb}?queries={queries}",
                                  headers={"Authorization": f"Bearer {get_token[0]}"})

            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert "first_name" in data[0]
            assert "last_name" in data[0]
            assert "email" in data[0]
            assert data[0]["first_name"] == "John"


@pytest.mark.asyncio
async def test_search_contact_by_lastname(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        async with TestingSessionLocal() as session:
            attrb = "wam"
            queries = await rep_contacts.search_contact_by_lastname(attrb, session)

            response = client.get(f"/api/search/by_lastname/{attrb}?queries={queries}",
                                  headers={"Authorization": f"Bearer {get_token[0]}"})

            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert "first_name" in data[0]
            assert "last_name" in data[0]
            assert "email" in data[0]
            assert data[0]["last_name"] == "Kwame"


@pytest.mark.asyncio
async def test_search_contact_by_email(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        async with TestingSessionLocal() as session:
            attrb = "wooo"
            queries = await rep_contacts.search_contact_by_email(attrb, session)

            response = client.get(f"/api/search/by_email/{attrb}?queries={queries}",
                                  headers={"Authorization": f"Bearer {get_token[0]}"})

            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert "first_name" in data[0]
            assert "last_name" in data[0]
            assert "email" in data[0]
            assert data[0]["email"] == "wooooooohn@ahtung.de"


@pytest.mark.asyncio
async def test_search_contact_query(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        async with TestingSessionLocal() as session:
            attrb = "ohn"
            queries = await rep_contacts.search_contact_query(attrb, session)

            response = client.get(f"/api/search/by_query/{attrb}?queries={queries}",
                                  headers={"Authorization": f"Bearer {get_token[0]}"})

            assert response.status_code == 200
            data = response.json()
            assert len(data) > 0
            assert "first_name" in data[0]
            assert "last_name" in data[0]
            assert "email" in data[0]
            assert data[0]["first_name"] == "John"
            assert data[0]["last_name"] == "Bon Jovi"
            assert data[0]["email"] == "john.jovi@undergraund.tv"

            assert "first_name" in data[1]
            assert "last_name" in data[1]
            assert "email" in data[1]
            assert data[1]["first_name"] == "Lenny"
            assert data[1]["last_name"] == "Wolf"
            assert data[1]["email"] == "wooooooohn@ahtung.de"
