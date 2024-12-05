import json
import typing
import socket
import logging
import dataclasses
import collections


Handler = typing.Callable[["Ctx", "Request"], "Response"]
Ctx = dict[str, typing.Any]
# Middleware here does not operate like a typical middleware you find in other frameworks:
#   - it only gets called once before the handler
#   - its sole task is to modify the context dictionary
#       - For example, it can be used to authenticate the user and add the user object to the context
#   - optionally, it can return a response to short-circuit the request, serving as a guard
Middleware = typing.Callable[["Ctx", "Request"], typing.Optional["Response"]]

Status = collections.namedtuple("Status", ["code", "message"])
Status_200_OK = Status(200, "OK")
Status_400_BAD_REQUEST = Status(400, "Bad Request")
Status_401_UNAUTHORIZED = Status(401, "Unauthorized")
Status_403_FORBIDDEN = Status(403, "Forbidden")
Status_404_NOT_FOUND = Status(404, "Not Found")
Status_409_CONFLICT = Status(409, "Conflict")
Status_500_INTERNAL_SERVER_ERROR = Status(500, "Internal Server Error")


@dataclasses.dataclass
class Response:
    body: str
    status: Status
    content_type: str

    headers: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def from_json(body: dict, status=Status_200_OK) -> "Response":
        """
        Create a new response from a JSON body.

        :param body: The body of the response.
        :param status: The status of the response.

        :return: The response object.
        """

        return Response(
            body=json.dumps(body),
            status=status,
            content_type="application/json",
        )

    @staticmethod
    def from_text(body: str, status=Status_200_OK) -> "Response":
        """
        Create a new response from a text body.

        :param body: The body of the response.
        :param status: The status of the response.

        :return: The response object.
        """

        return Response(
            body=body,
            status=status,
            content_type="text/plain",
        )

    @staticmethod
    def validation_error(body: str, status=Status_400_BAD_REQUEST) -> "Response":
        """
        Create a new response from a text body.

        :param body: The body of the response.
        :param status: The status of the response.

        :return: The response object.
        """

        return Response(
            body=body,
            status=status,
            content_type="application/json",
        )

    def set_header(self, key: str, value: str) -> None:
        """
        Set a header in the response.

        :param key: The key of the header.
        :param value: The value of the header.
        """

        self.headers[key] = value

    def set_cookie(self, key: str, value: str, expires: int = 60 * 15) -> None:
        """
        Set the "Set-Cookie" header in the response.

        :param key: The key of the cookie.
        :param value: The value of the cookie.
        :param expires: The expiration time of the cookie in seconds.
        """

        if "Set-Cookie" not in self.headers:
            self.headers["Set-Cookie"] = ""
        self.headers[
            "Set-Cookie"
        ] += f"{key}={value}; Max-Age={expires}; Path=/; HttpOnly; Secure"

    def to_bytes(self) -> bytes:
        """
        Convert the response to bytes.

        :return: The response as bytes.
        """

        _body = f"HTTP/1.1 {self.status.code} {self.status.message}\r\n"
        _body += f"Content-Type: {self.content_type}\r\n"
        _body += f"Content-Length: {len(self.body)}\r\n"
        for key, value in self.headers.items():
            _body += f"{key}: {value}\r\n"
        _body += f"\r\n"
        _body += f"{self.body}"
        return _body.encode()

    def send(self, connection_socket: socket.socket) -> None:
        """
        Send the response to the client.

        :param connection_socket: The socket to send the response to.
        """

        connection_socket.send(self.to_bytes())


@dataclasses.dataclass
class Request:
    method: str
    path: str
    version: str
    body: typing.Any
    params: dict[str, str] = dataclasses.field(default_factory=dict)
    headers: dict[str, str] = dataclasses.field(default_factory=dict)
    cookies: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def from_bytes(message: bytes) -> "Request":
        """
        Create a new request from bytes.

        :param message: The message to parse.
        """

        _raw_header, _body = message.decode().split("\r\n\r\n", 1)
        _header_first_line, *_headers = _raw_header.strip().split("\r\n")
        _method, _path, _version = _header_first_line.strip().split()

        _params = dict()
        if "?" in _path:
            _path, _raw_params = _path.split("?", 1)
            _params = dict([param.split("=") for param in _raw_params.split("&")])

        _headers = dict([header.strip().split(": ", 1) for header in _headers])

        if _headers.get("Content-Type", "") == "application/json":
            _body = json.loads(_body) if _body else None

        _cookies = dict()
        if "Cookie" in _headers:
            _cookies = dict(
                [cookie.split("=") for cookie in _headers["Cookie"].split("; ")]
            )

        return Request(
            method=_method,
            path=_path,
            version=_version,
            body=_body,
            headers=_headers,
            params=_params,
            cookies=_cookies,
        )

    def get_route(self) -> str:
        """
        Get the route name of the request.

        :return: The route name of the request, used in the router.
        """

        return f"{self.method}:{self.path}"

    def __repr__(self) -> str:
        message = "Request("
        message += f"  method={self.method}, "
        message += f"  path={self.path}, "
        message += f"  version={self.version}, "
        message += f"  body={self.body}, "
        message += f"  params={self.params}, "
        message += f"  headers={self.headers}, "
        message += ")"
        return message


class Router:
    middlewares: list[Handler]
    routes: dict[str, Handler]
    # Which middlewares should be applied to which routes
    route_middlewares: dict[str, list[Middleware]]

    def __init__(self):
        self.middlewares = list()
        self.routes = dict()
        self.route_middlewares = dict()

    @staticmethod
    def not_found(ctx: Ctx, req: Request) -> Response:
        """
        Default handler for when a route is not found.
        """

        data = {"error": "Not Found"}
        res = Response.from_json(data, status=Status_404_NOT_FOUND)
        return res

    @staticmethod
    def debug(ctx: Ctx, req: Request) -> Response:
        """
        Debug handler for debugging purposes. Echos the request back to the client.

        :param req: The request to echo.

        :return: The response with the request body.
        """

        res = Response.from_json(
            {
                "ctx": ctx,
                "method": req.method,
                "path": req.path,
                "version": req.version,
                "body": req.body,
                "headers": req.headers,
            }
        )
        return res

    def register_middleware(self, middleware: Middleware) -> None:
        """
        Register a new middleware. Middlewares will be applied to all routes registered after this.
        """

        self.middlewares.append(middleware)

    def register_route(self, method: str, path: str, handler: Handler) -> None:
        """
        Register a new route. All middlewares registered before this will be applied to this route.

        :param method: The HTTP method of the route.
        :param path: The path of the route.
        :param handler: The handler of the route.
        """

        self.routes[f"{method}:{path}"] = handler

        self.route_middlewares[f"{method}:{path}"] = list()
        for middleware in self.middlewares:
            self.route_middlewares[f"{method}:{path}"].append(middleware)

    def route(self, req: Request) -> Response:
        """
        Applies the middlewares to the request and routes it to the correct handler.

        :param req: The request to route.

        :return: The response from the handler.
        """

        ctx = dict()
        for middleware in self.route_middlewares.get(req.get_route(), list()):
            res = middleware(ctx, req)
            if res:
                return res
        return self.routes.get(req.get_route(), self.not_found)(ctx, req)


class Server:
    logger: logging.Logger

    server_socket: socket.socket
    server_port: int

    router = Router()

    def __init__(
        self,
        server_port: int = 6969,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        """
        Create a new server instance.

        :param server_port: The port the server should run on.
        :param logger: The logger to use.
        """

        self.logger = logger

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_port = server_port

    def register_debug_route(self) -> None:
        """
        Register route /debug for debugging purposes. /debug echos the request back to the client.
        """

        self.router.register_route("GET", "/debug", Router.debug)
        self.router.register_route("POST", "/debug", Router.debug)
        self.router.register_route("PUT", "/debug", Router.debug)
        self.router.register_route("PATCH", "/debug", Router.debug)
        self.router.register_route("DELETE", "/debug", Router.debug)

    def bind(self) -> None:
        """
        Bind the server to the port and start listening for connections.
        """

        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(1)
        self.logger.info("The server is ready to receive")

    def run(self) -> None:
        """
        The main loop of the server. This will block the execution of the program.
        """

        while True:
            connection_socket, client_address = self.server_socket.accept()
            self.logger.info(f"{client_address}: Connection established")

            message = connection_socket.recv(4096)

            request = Request.from_bytes(message)
            self.logger.debug(f"{client_address}: Received request: {request}")

            try:
                response = self.router.route(request)
            except Exception as e:
                self.logger.exception(f"{client_address}: {e}")
                response = Response.from_text(
                    "Internal Server Error", status=Status_500_INTERNAL_SERVER_ERROR
                )

            self.logger.info(
                f"{client_address}: Responding with status {response.status}"
            )
            self.logger.debug(f"{client_address}: Response: {response.body}")

            self.logger.debug(f"{client_address}: Sending response")
            response.send(connection_socket)
            self.logger.debug(f"{client_address}: Response sent")

            connection_socket.shutdown(socket.SHUT_WR)

            # Drain the socket, see: https://blog.netherlabs.nl/articles/2009/01/18/the-ultimate-so_linger-page-or-why-is-my-tcp-not-reliable
            for _ in range(69420):
                connection_socket.recv(4096)

            connection_socket.close()
