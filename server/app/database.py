import bson
import typing
import logging
import pymongo
import pymongo.database
import pymongo.collection
import pydantic


RequiredId = typing.Annotated[
    str,
    pydantic.PlainValidator(lambda value: str(value)),
    pydantic.WrapSerializer(
        lambda value, handler, info: (
            bson.ObjectId(value) if info.context == "objectid" and value else value
        )
    ),
    pydantic.Field(min_length=24, max_length=24),
]

OptionalId = typing.Annotated[
    RequiredId | None,
    pydantic.Field(default=None),
]


class DbDumper(pydantic.BaseModel):
    @staticmethod
    def from_db(doc: dict) -> dict:
        model_dump = doc.copy()
        for key, value in model_dump.items():
            if isinstance(value, bson.ObjectId):
                model_dump[key] = str(value)
        if "_id" in model_dump:
            model_dump["id"] = str(model_dump["_id"])
            del model_dump["_id"]
        return model_dump

    @staticmethod
    def to_db(model: pydantic.BaseModel, include_id: bool = False) -> dict:
        dump = model.model_dump(context="objectid")
        if "id" in dump:
            if include_id:
                dump["_id"] = dump["id"]
            del dump["id"]
        return dump


class Database:
    logger: logging.Logger

    client: pymongo.MongoClient
    db: pymongo.database.Database

    def __init__(
        self,
        uri: str,
        database_name: str,
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        """
        Initialize the database connection.

        :param uri: The URI of the MongoDB database.
        :param database_name: The name of the database.
        :param logger: The logger to use.
        """
        self.logger = logger
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[database_name]

    def get_collection(self, collection_name: str) -> pymongo.collection.Collection:
        """
        Get a collection from the database, with timezone awareness.

        :param collection_name: The name of the collection.

        :return: The collection.
        """

        codec_options = bson.CodecOptions(tz_aware=True)
        return self.db.get_collection(collection_name, codec_options=codec_options)
