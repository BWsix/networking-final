from app.database import DbDumper, OptionalId, RequiredId
from bson import ObjectId
from typing import Annotated
from pydantic import EmailStr, Field, SecretStr
from app import utils


class Credentials(DbDumper):
    username: str
    password: SecretStr

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(DbDumper):
    id: OptionalId
    username: str
    email: EmailStr
    hashed_password: Annotated[str | None, Field(default=None)]

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateUser(User):
    password: SecretStr

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Mail(DbDumper):
    id: OptionalId
    to: str
    subject: str
    body: str
    user_id: RequiredId

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
