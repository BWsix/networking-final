from app import repository, models, utils
import json
from app import framework, mailer
from app.framework import Response, Request, Ctx
from pydantic import ValidationError


repo = repository.MongoRepository()


def get_me(ctx: Ctx, req: Request) -> Response:
    """
    Return the current user.

    Response body:
    ```json
    {
        "id": "string",
        "username": "string",
        "email": "string"
    }
    ```
    """

    user: models.User = ctx.get("user")
    return Response.from_json(user.model_dump(exclude={"hashed_password"}))


def get_users(ctx: Ctx, req: Request) -> Response:
    """
    Get all users.

    Response body:
    ```json
    [
        {
            "id": "string",
            "username": "string",
            "email": "string"
        }
    ]
    ```
    """

    users = [user.model_dump(exclude={"hashed_password"}) for user in repo.get_users()]
    return Response.from_json(users)


def create_user(ctx: Ctx, req: Request) -> Response:
    """
    Create a new user.

    Request body:
    ```json
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    ```

    Response body:
    ```json
    {
        "id": "string",
        "username": "string",
        "email": "string"
    }
    ```

    Responses:
    - 200: User created successfully.
    - 400: Invalid request body.
    - 409: User already exists.
    """

    try:
        user = models.CreateUser.model_validate(req.body)
        user.hashed_password = utils.hash_password(user.password.get_secret_value())
    except ValidationError as e:
        return Response.validation_error(e.json())

    duplicate_field = ""
    if repo.get_user({"username": user.username}):
        duplicate_field = "username"

    if duplicate_field:
        body = {
            "error": f"{duplicate_field.capitalize()} already taken",
            "field": duplicate_field,
        }
        return Response.from_json(body, status=framework.Status_409_CONFLICT)

    user = repo.create_user(
        models.User(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
        )
    )
    return Response.from_json(user.model_dump(exclude={"hashed_password"}))


def login_user(ctx: Ctx, req: Request) -> Response:
    """
    Login a user. Set a cookie with RAW USER DATA.

    Request body:
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```

    Responses:
    - 200: User logged in successfully.
    - 400: Invalid request body.
    - 401: Invalid password.
    - 404: User not found.
    """
    try:
        credentials = models.Credentials.model_validate(req.body)
    except ValidationError as e:
        return Response.validation_error(e.json())

    user = repo.get_user({"username": credentials.username})
    if not user:
        return Response.from_text(
            "User not found", status=framework.Status_404_NOT_FOUND
        )

    if not utils.verify_password(
        credentials.password.get_secret_value(), user.hashed_password
    ):
        return Response.from_text(
            "Invalid password", status=framework.Status_401_UNAUTHORIZED
        )

    dumped_user = json.dumps(user.model_dump(exclude={"hashed_password"}))

    res = Response.from_json({"jwt": utils.build_jwt(dumped_user)})
    return res


def send_mail(ctx: Ctx, req: Request) -> Response:
    """
    Send an email.

    Request body:
    ```json
    {
        "to": "string",
        "subject": "string",
        "body": "string"
    }
    ```

    Responses:
    - 200: Email sent successfully.
    - 400: Invalid request body.
    - 500: Email not sent.
    """

    user: models.User = ctx.get("user")

    try:
        mailer.send(user.email, req.body["to"], req.body["subject"], req.body["body"])

        mail = models.Mail(
            user_id=user.id,
            to=req.body["to"],
            subject=req.body["subject"],
            body=req.body["body"],
        )
        repo.create_mail(mail)

        return Response.from_text("Email sent")
    except Exception as e:
        return Response.from_text(
            "Email not sent", status=framework.Status_500_INTERNAL_SERVER_ERROR
        )

def get_mails(ctx: Ctx, req: Request) -> Response:
    """
    Get all mails send by the current user.

    Response body:
    ```json
    [
        {
            "id": "string",
            "to": "string",
            "subject": "string",
            "body": "string"
        }
    ]
    ```
    """

    user: models.User = ctx.get("user")

    try:
        mails = [mail.model_dump() for mail in repo.get_mails_by_user_id(user.id)]
        return Response.from_json(mails)
    except Exception as e:
        return Response.from_text(
            "Unexpected Error", status=framework.Status_500_INTERNAL_SERVER_ERROR
        )
