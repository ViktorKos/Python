import re
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=32)
    last_name: str = Field(min_length=3, max_length=32)
    email: EmailStr = Field(min_length=8, max_length=64)
    phone_number: str
    birth_date: date

    @validator('phone_number')
    def validate_phone_number(cls, value):
        if not value.isdigit():
            raise ValueError('Phone number must contain only digits.')
        return value

    @validator('birth_date')
    def validate_birth_date(cls, value):
        if not isinstance(value, date):
            raise ValueError('Invalid date format.')

        date_str = str(value)
        date_format = '%Y-%m-%d'  # or another format that matches your input
        return datetime.strptime(date_str, date_format).date()


class ContactUpdateSchema(ContactSchema):
    pass


class ContactResponseSchema(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birth_date: date

    class Config:
        from_attributes = True
