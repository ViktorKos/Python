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
    """
   The get_contacts function returns a list of contacts.
       The limit and offset parameters are used to paginate the results.
       The user parameter is used to get only the contacts for that user.

   :param limit: int: Limit the number of contacts returned
   :param ge: Specify that the limit must be greater than or equal to 10
   :param le: Set the maximum value of the limit parameter
   :param offset: int: Specify the number of records to skip
   :param ge: Set a minimum value for the limit parameter
   :param db: AsyncSession: Get the database connection
   :param user: User: Get the current user
   :return: A list of contacts
   :doc-author: Trelent
   """

    try:
        contacts = await rep_contacts.get_contacts(limit, offset, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{contact_id}", response_model=ContactResponseSchema)
async def get_contact(contact_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is used to retrieve a single contact from the database.
    It takes an integer as its only argument, which represents the ID of the contact
    to be retrieved. It returns a Contact object.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: The contact object with the given id
    :doc-author: Trelent
    """

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
    """
    The create_contact function creates a new contact in the database.
        It takes a ContactSchema object as input, and returns the newly created contact.
        The user who is creating this contact must be logged in.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """

    try:
        contact = await rep_contacts.create_contact(body, db)
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{contact_id}")
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1),
                         db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        It takes an id, body and db as parameters. The id is used to find the contact in the database,
        while body contains all of the information that will be updated for that contact.

        Args:

    :param body: ContactSchema: Get the data from the request body
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user from the auth_service
    :return: The contact that was updated
    :doc-author: Trelent
    """

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
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Specify the contact_id of the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the auth_service
    :return: The deleted contact
    :doc-author: Trelent
    """

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
    """
    The search_contact_by_firstname function searches for contacts by first name.
        The search_contact_by_firstname function is a GET request that takes in the contact's first name as a parameter.
        It returns all contacts with the given first name.

    :param contact_first_name: str: Pass the contact's first name to the function
    :param description: Describe the parameter in the openapi documentation
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """

    try:
        contacts = await rep_contacts.search_contact_by_firstname(contact_first_name, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router_search.get("/by_lastname/{contact_last_name}", response_model=list[ContactResponseSchema])
async def search_contact_by_lastname(contact_last_name: str = Path(..., description="Прізвище контакту"),
                                     db: AsyncSession = Depends(get_async_session),
                                     user: User = Depends(auth_service.get_current_user)):
    """
   The search_contact_by_lastname function allows you to search for a contact by last name.

   :param contact_last_name: str: Pass the contact's last name to the function
   :param description: Describe the parameter in the documentation
   :param db: AsyncSession: Get the database session
   :param user: User: Identify the user who is logged in
   :return: A list of contacts
   :doc-author: Trelent
   """

    try:
        contacts = await rep_contacts.search_contact_by_lastname(contact_last_name, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router_search.get("/by_email/{contact_email}", response_model=list[ContactResponseSchema])
async def search_contact_by_email(contact_email: str = Path(..., description="Електронна адреса контакту"),
                                  db: AsyncSession = Depends(get_async_session),
                                  user: User = Depends(auth_service.get_current_user)):
    """
    The search_contact_by_email function searches for a contact by email.

    :param contact_email: str: Get the email of the contact we want to search for
    :param description: Describe the parameter in the openapi documentation
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """

    try:
        contacts = await rep_contacts.search_contact_by_email(contact_email, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router_search.get("/by_query/{value}", response_model=list[ContactResponseSchema])
async def search_contact_query(
        value: str = Path(..., description="Здійснює пошук у полях контакту: Ім'я, Прізвище та Електронна адреса"),
        db: AsyncSession = Depends(get_async_session), user: User = Depends(auth_service.get_current_user)):
    """
    The search_contact_query function is used to search for contacts by name, surname and email.
        The function takes a string value as an argument and returns a list of contacts that match the search criteria.

    :param value: str: Search for a contact in the database
    :param description: Describe the endpoint in the openapi documentation
    :param Прізвище та Електронна адреса&quot;): Search for a contact by surname and email
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """

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
    """
    The search_contact_by_birthdate function is used to search for contacts by their birthday.

    :param shift_days: int: Specify the number of days to search for
    :param description: Describe the parameter in the documentation
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Identify the user who is logged in
    :return: A list of contacts
    :doc-author: Trelent
    """
    try:
        contacts = await rep_contacts.search_contact_by_birthdate(shift_days, db)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
