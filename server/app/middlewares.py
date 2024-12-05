# Middleware = typing.Callable[["Ctx", "Request"], None]

from pydantic import ValidationError
from app.framework import Request, Ctx, Response, Status_401_UNAUTHORIZED
import json
from app import models, utils, logger


def inject_user(ctx: Ctx, req: Request):
    try:
        _user = utils.verify_jwt(req.cookies.get("token"))
        logger.app.debug(f"inject_user - User raw string: {_user}")
    except utils.InvalidToken:
        return Response.from_text("Unauthorized", status=Status_401_UNAUTHORIZED)

    try:
        _user = json.loads(_user)
        logger.app.debug(f"inject_user - User dict: {_user}")
    except json.JSONDecodeError:
        return Response.from_text("Unauthorized", status=Status_401_UNAUTHORIZED)

    try:
        user = models.User.model_validate(_user)
        logger.app.debug(f"inject_user - User object: {user}")
    except ValidationError as e:
        return Response.from_text("Unauthorized", status=Status_401_UNAUTHORIZED)

    ctx["user"] = user
    return None
