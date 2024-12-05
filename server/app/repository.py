from pymongo.collection import Collection
from bson import ObjectId
from app import database, logger, config
from app.models import Post, User


class MongoRepository:
    db: database.Database
    users_collection: Collection
    posts_collection: Collection

    def __init__(self):
        self.db = database.Database(
            config.settings.MONGODB_URI,
            config.settings.MONGODB_DATABASE,
            logger=logger.db,
        )
        self.users_collection = self.db.get_collection("users")
        self.posts_collection = self.db.get_collection("posts")

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

    def create_post(self, post: Post) -> Post:
        post_dict = Post.to_db(post)
        result = self.posts_collection.insert_one(post_dict)
        post.id = str(result.inserted_id)
        return post

    def get_post(self, post_id: str) -> Post:
        post_dict = self.posts_collection.find_one({"_id": ObjectId(post_id)})
        if post_dict:
            return Post(**Post.from_db(post_dict))
        return None
