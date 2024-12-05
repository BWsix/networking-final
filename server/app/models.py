from app.database import DbDumper, OptionalId, RequiredId
from bson import ObjectId
from typing import Annotated
from pydantic import EmailStr, Field, SecretStr
from app import utils


class Credentials(DbDumper):
    username: str
    password: SecretStr

    def get_hashed_password(self) -> str:
        return utils.hash_password(self.password.get_secret_value())

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(DbDumper):
    id: OptionalId
    username: str
    email: EmailStr
    hashed_password: Annotated[str | None, Field(default=None)]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateUser(User):
    password: SecretStr

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Post(DbDumper):
    id: OptionalId
    title: str
    content: str
    author_id: RequiredId

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}