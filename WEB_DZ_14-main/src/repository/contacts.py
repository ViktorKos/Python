from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.schemas.contact_schemas import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of records to skip before returning results
    :param db: AsyncSession: Pass the database session into the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """

    statement = select(Contact).offset(offset).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    """
    The get_contact function is used to retrieve a contact from the database.
    It takes in an integer representing the id of the contact, and returns a Contact object.
    If no such contact exists, it will return None.

    :param contact_id: int: Get the contact with that id
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user object from the database
    :return: A contact object
    :doc-author: Trelent
    """

    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    return contact.scalar_one_or_none()


async def get_contacts_all(limit: int, offset: int, db: AsyncSession):
    """
    The get_contacts_all function returns a list of all contacts in the database.
    The limit and offset parameters are used to paginate the results.


    :param limit: int: Limit the number of results returned
    :param offset: int: Set the offset for the query
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    statement = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(statement)
    return contacts.scalars().all()


async def create_contact(session: AsyncSession, contact_data: ContactSchema, user: User) -> Contact:
    new_contact_data = contact_data.dict(exclude_unset=True)
    new_contact_data['user_id'] = user.id

    async with session.begin():
        # Використовуйте метод create, який надає пакет SQLAlchemy ORM
        new_contact = Contact(**new_contact_data)
        session.add(new_contact)

    return new_contact




async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactSchema): A ContactSchema object containing all of the information for updating a Contact object.  This is passed as JSON data in an HTTP request body, and it is deserialized into this schema by Pydantic before being passed to this function.  See models/contact_schema for more details on what fields are required or optional when creating or updating contacts via ReST API calls.

    :param contact_id: int: Identify the contact to update
    :param body: ContactSchema: Get the information from the body of the request
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user can only update their own contacts
    :return: The contact object
    :doc-author: Trelent
    """

    statement = select(Contact).filter_by(id=contact_id)
    result = await db.execute(statement)
    contact = result.scalar_one_or_none()
    if contact:
        contact_data = body.dict(exclude_unset=True)
        for field, value in contact_data.items():
            setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to delete
    :param db: AsyncSession: Pass the database session into the function
    :param user: User: Pass the user object to the function
    :return: A contact object
    :doc-author: Trelent
    """

    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contact_by_firstname(contact_first_name: str, db: AsyncSession):
    """
    The search_contact_by_firstname function searches the database for contacts with a first name that matches the search string.
        Args:
            contact_first_name (str): The first name of the contact to be searched for.
            db (AsyncSession): The database connection object.

    :param contact_first_name: str: Pass the contact first name to search for
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """

    statement = select(Contact).where(Contact.first_name.ilike(f'%{contact_first_name}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_lastname(contact_last_name: str, db: AsyncSession):
    """
    The search_contact_by_lastname function searches the database for contacts with a last name that matches the search string.
        Args:
            contact_last_name (str): The last name of the contact to be searched for.
            db (AsyncSession): The database connection object.

    :param contact_last_name: str: Pass the contact last name to search for
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    statement = select(Contact).where(Contact.last_name.ilike(f'%{contact_last_name}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_email(contact_email: str, db: AsyncSession):
    """
    The search_contact_by_lastname function searches the database for contacts with a last name that matches the search string.
        Args:
            contact_last_name (str): The last name of the contact to be searched for.
            db (AsyncSession): The database connection object.

    :param contact_last_name: str: Search for a contact by last name
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """

    statement = select(Contact).where(Contact.email.ilike(f'%{contact_email}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_query(query: str, db: AsyncSession):
    """
    The search_contact_query function is a complex search function that searches for contacts by first name, last name, and email.
    It takes in a query string and an AsyncSession object as parameters. It returns the result of the database query.

    :param query: str: Search for contacts that have a first name, last name or email
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """

    statement = select(Contact).where(or_(
        Contact.first_name.ilike(f'%{query}%'),
        Contact.last_name.ilike(f'%{query}%'),
        Contact.email.ilike(f'%{query}%')
    ))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_field(field_name: str, field_value: str, db: AsyncSession):
    """
    The search_contact_by_field function searches for contacts by a specific field.

    :param field_name: str: Specify the name of the field to search for
    :param field_value: str: Specify the value of the field to search for
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    statement = select(Contact).where(getattr(Contact, field_name).ilike(f'%{field_value}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_birthdate(forward_shift_days: int, db: AsyncSession):
    """
   The search_contact_by_birthdate function searches for contacts whose birthdays are within the next &lt;forward_shift_days&gt; days.
   The function returns a list of Contact objects that match the search criteria.

   :param forward_shift_days: int: Specify the number of days to shift forward from today
   :param db: AsyncSession: Pass the database connection to the function
   :return: A list of contact objects
   :doc-author: Trelent
   """

    if forward_shift_days > 364:
        raise HTTPException(status_code=422, detail="The <forward_shift_days> parameter should be 364 or less.")

    current_date = datetime.now().date()
    end_of_shift_date = current_date + timedelta(forward_shift_days)

    statement = (
        select(Contact)
        .where(
            or_(
                and_(
                    func.extract("month", Contact.birth_date) == current_date.month,
                    func.extract("day", Contact.birth_date) >= current_date.day,
                    func.extract("day", Contact.birth_date) <= end_of_shift_date.day
                ),
                and_(
                    func.extract("month", Contact.birth_date) == end_of_shift_date.month,
                    func.extract("day", Contact.birth_date) <= end_of_shift_date.day
                ),
            )
        )
    )

    result = await db.execute(statement)

    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def _get_contact_by_id(contact_id: int, db: AsyncSession):
    """
    The _get_contact_by_id function takes in an id and returns a contact object.

    :param contact_id: int: Specify the id of the contact
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    statement = select(Contact).filter_by(id=contact_id)
    result = await db.execute(statement)
    if result:
        return await result.scalar_one_or_none()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")
