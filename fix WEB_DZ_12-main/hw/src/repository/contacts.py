from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact
from src.schemas.contact_schemas import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    statement = select(Contact).offset(offset).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    contact_data = body.dict(exclude_unset=True)
    contact = Contact(**contact_data)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession):
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
    statement = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(statement)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contact_by_firstname(contact_first_name: str, db: AsyncSession):
    statement = select(Contact).where(Contact.first_name.ilike(f'%{contact_first_name}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_lastname(contact_last_name: str, db: AsyncSession):
    statement = select(Contact).where(Contact.last_name.ilike(f'%{contact_last_name}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_email(contact_email: str, db: AsyncSession):
    statement = select(Contact).where(Contact.email.ilike(f'%{contact_email}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_query(query: str, db: AsyncSession):
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
    statement = select(Contact).where(getattr(Contact, field_name).ilike(f'%{field_value}%'))
    result = await db.execute(statement)
    if result:
        return result.scalars().all()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")


async def search_contact_by_birthdate(forward_shift_days: int, db: AsyncSession):
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
    statement = select(Contact).filter_by(id=contact_id)
    result = await db.execute(statement)
    if result:
        return await result.scalar_one_or_none()
    raise HTTPException(status_code=204, detail="No Content. The Search did not get results.")
