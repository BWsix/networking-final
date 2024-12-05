import socket

import json
import typing
import logging
import dataclasses
import collections


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

Status = collections.namedtuple("Status", ["code", "message"])


@dataclasses.dataclass
class Response:
    body: str
    status: Status
    content_type: str

    headers: dict[str, str] = dataclasses.field(default_factory=dict)

    @staticmethod
    def from_json(body: dict, status=Status(200, "OK")) -> "Response":
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
    def from_text(body: str, status=Status(200, "OK")) -> "Response":
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

    def set_header(self, key: str, value: str) -> None:
        """
        Set a header in the response.

        :param key: The key of the header.
        :param value: The value of the header.
        """

        self.headers[key] = value

    def set_cookie(self, key: str, value: str) -> None:
        """
        Set the "Set-Cookie" header in the response.

        :param key: The key of the cookie.
        :param value: The value of the cookie.
        """

        if "Set-Cookie" not in self.headers:
            self.headers["Set-Cookie"] = ""
        self.headers["Set-Cookie"] += f"{key}={value}; "

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

        return Request(
            method=_method,
            path=_path,
            version=_version,
            body=_body,
            headers=_headers,
            params=_params,
        )

    def get_route(self) -> str:
        """
        Get the route name of the request.

        :return: The route name of the request, used in the router.
        """

        return f"{self.method}:{self.path}"

    def __repr__(self) -> str:
        message = "Request(\n"
        message += f"  method={self.method},\n"
        message += f"  path={self.path},\n"
        message += f"  version={self.version},\n"
        message += f"  body={self.body},\n"
        message += f"  params={self.params},\n"
        message += f"  headers={self.headers}\n"
        message += ")"
        return message


Handler: typing.TypeAlias = typing.Callable[[Request], Response]


class Router:
    routes: dict[str, Handler]

    def __init__(self):
        self.routes = {}

    @staticmethod
    def not_found(req: Request) -> Response:
        """
        Default handler for when a route is not found.
        """

        data = {"error": "Not Found"}
        res = Response.from_json(data)
        return res

    @staticmethod
    def debug(req: "Request") -> Response:
        """
        Debug handler for debugging purposes. Echos the request back to the client.

        :param req: The request to echo.

        :return: The response with the request body.
        """

        res = Response.from_json(
            {
                "method": req.method,
                "path": req.path,
                "version": req.version,
                "body": req.body,
                "headers": req.headers,
            }
        )
        return res

    def register_route(self, method: str, path: str, handler: Handler) -> None:
        """
        Register a new route.

        :param method: The HTTP method of the route.
        :param path: The path of the route.
        :param handler: The handler of the route.
        """

        self.routes[f"{method}:{path}"] = handler

    def route(self, req: Request) -> Response:
        """
        Route a request to the correct handler.

        :param req: The request to route.

        :return: The response from the handler.
        """

        return self.routes.get(req.get_route(), self.not_found)(req)


class Server:
    server_socket: socket.socket
    server_port: int

    router = Router()

    def __init__(self, server_port: int = 6969) -> None:
        """
        Create a new server instance.

        :param server_port: The port the server should run on.
        """

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
        logger.info("The server is ready to receive")

    def run(self) -> None:
        """
        The main loop of the server. This will block the execution of the program.
        """

        while True:
            connection_socket, client_address = self.server_socket.accept()
            logger.info(f"{client_address}: Connection established")

            message = connection_socket.recv(4096)

            request = Request.from_bytes(message)
            logger.debug(f"{client_address}: Received request: {request}")

            response = self.router.route(request)
            logger.info(f"{client_address}: Responding with status {response.status}")
            logger.debug(f"{client_address}: Response: {response.body}")

            logger.debug(f"{client_address}: Sending response")
            response.send(connection_socket)
            logger.debug(f"{client_address}: Response sent")

            connection_socket.shutdown(socket.SHUT_WR)

            # Drain the socket, see: https://blog.netherlabs.nl/articles/2009/01/18/the-ultimate-so_linger-page-or-why-is-my-tcp-not-reliable
            for _ in range(69420):
                connection_socket.recv(4096)

            connection_socket.close()
