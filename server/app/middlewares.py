# Middleware = typing.Callable[["Ctx", "Request"], None]

from pydantic import ValidationError
from app.framework import Request, Ctx, Response, Status_401_UNAUTHORIZED
import json
from app import models, utils, logger


def say_ok_to_preflight_requests(ctx: Ctx, req: Request):
    if req.method == "OPTIONS":
        return Response.from_text("OK")


def inject_user(ctx: Ctx, req: Request):
    try:
        _user = utils.verify_jwt(req.headers.get("Authorization"))
        logger.app.info(f"inject_user - User raw string: {_user}")
    except utils.InvalidToken:
        return Response.from_text("Unauthorized", status=Status_401_UNAUTHORIZED)

    try:
        _user = json.loads(_user)
        logger.app.info(f"inject_user - User dict: {_user}, type: {type(_user)}")
    except json.JSONDecodeError:
        return Response.from_text("Unauthorized", status=Status_401_UNAUTHORIZED)

    try:
        user = models.User.model_validate(_user)
        logger.app.info(f"inject_user - User object: {user}")
    except ValidationError as e:
        logger.framework.info(f"inject_user - ValidationError: {e}")
        return Response.from_text("Unauthorized", status=Status_401_UNAUTHORIZED)

    ctx["user"] = user
