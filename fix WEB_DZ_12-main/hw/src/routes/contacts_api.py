from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_async_session
from src.entity.models import User
from src.repository import contacts as rep_contacts
from src.schemas.contact_schemas import ContactSchema, ContactResponseSchema
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=list[ContactResponseSchema])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_async_session),
                       user: User = Depends(auth_service.get_current_user)):
    try:
        contacts = await rep_contacts.get_contacts(limit, offset, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_contact(contact_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(auth_service.get_current_user)):
    try:
        contact = await rep_contacts.get_contact(contact_id, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ENTITY NOT FOUND.")
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=ContactResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(auth_service.get_current_user)):
    try:
        contact = await rep_contacts.create_contact(body, db)
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{contact_id}")
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(auth_service.get_current_user)):
    try:
        contact = await rep_contacts.update_contact(contact_id, body, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ENTITY NOT FOUND.")
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(auth_service.get_current_user)):
    try:
        contact = await rep_contacts.delete_contact(contact_id, db)
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


router_search = APIRouter(prefix='/contacts/search', tags=['search'])


@router_search.get("/by_firstname/{contact_first_name}", response_model=list[ContactResponseSchema])
async def search_contact_by_firstname(contact_first_name: str = Path(..., description="Ім'я контакту"),
                                      db: AsyncSession = Depends(get_async_session),
                                      user: User = Depends(auth_service.get_current_user)):
    try:
        contacts = await rep_contacts.search_contact_by_firstname(contact_first_name, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router_search.get("/by_lastname/{contact_last_name}", response_model=list[ContactResponseSchema])
async def search_contact_by_lastname(contact_last_name: str = Path(..., description="Прізвище контакту"),
                                     db: AsyncSession = Depends(get_async_session),
                                     user: User = Depends(auth_service.get_current_user)):
    try:
        contacts = await rep_contacts.search_contact_by_lastname(contact_last_name, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router_search.get("/by_email/{contact_email}", response_model=list[ContactResponseSchema])
async def search_contact_by_email(contact_email: str = Path(..., description="Електронна адреса контакту"),
                                  db: AsyncSession = Depends(get_async_session),
                                  user: User = Depends(auth_service.get_current_user)):
    try:
        contacts = await rep_contacts.search_contact_by_email(contact_email, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router_search.get("/by_query/{value}", response_model=list[ContactResponseSchema])
async def search_contact_query(
        value: str = Path(..., description="Здійснює пошук у полях контакту: Ім'я, Прізвище та Електронна адреса"),
        db: AsyncSession = Depends(get_async_session), user: User = Depends(auth_service.get_current_user)):
    try:
        contacts = await rep_contacts.search_contact_query(value, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


router_birthday = APIRouter(prefix='/birthday', tags=['birthday'])


@router_birthday.get("/{shift_days}", response_model=list[ContactResponseSchema])
async def search_contact_by_birthdate(shift_days: int = Path(..., description="Кількість найближчих днів у запитi"),
                                      db: AsyncSession = Depends(get_async_session),
                                      user: User = Depends(auth_service.get_current_user)):
    try:
        contacts = await rep_contacts.search_contact_by_birthdate(shift_days, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
