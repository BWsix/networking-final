from pymongo.collection import Collection
from bson import ObjectId
from app import database, logger, config
from app.models import Mail, User


class MongoRepository:
    db: database.Database
    users_collection: Collection
    mails_collection: Collection

    def __init__(self):
        self.db = database.Database(
            config.settings.MONGODB_URI,
            config.settings.MONGODB_DATABASE,
            logger=logger.db,
        )
        self.users_collection = self.db.get_collection("users")
        self.mails_collection = self.db.get_collection("mails")

    def create_user(self, user: User) -> User:
        user_dict = User.to_db(user)
        result = self.users_collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    def get_user(self, filter: dict) -> User:
        user_dict = self.users_collection.find_one(filter)
        if user_dict:
            return User(**User.from_db(user_dict))
        return None

    def get_users(self) -> list[User]:
        users_dict = self.users_collection.find()
        users = [User(**User.from_db(user_dict)) for user_dict in users_dict]
        return users

    def create_mail(self, mail: Mail) -> Mail:
        mail_dict = Mail.to_db(mail)
        result = self.mails_collection.insert_one(mail_dict)
        mail.id = str(result.inserted_id)
        return mail

    def get_mails_by_user_id(self, user_id: str) -> list[Mail]:
        mails_dict = self.mails_collection.find({"user_id": ObjectId(user_id)})
        mails = [Mail(**Mail.from_db(mail_dict)) for mail_dict in mails_dict]
        return mails

    def get_mail(self, mail_id: str) -> Mail:
        mail_dict = self.mails_collection.find_one({"_id": ObjectId(mail_id)})
        if mail_dict:
            return Mail(**Mail.from_db(mail_dict))
        return None
