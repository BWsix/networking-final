from app import handlers, logger, handlers
from app import framework


if __name__ == "__main__":
    server = framework.Server(logger=logger.framework)

    server.router.register_route("POST", "/user", handlers.create_user)
    server.router.register_route("GET", "/users", handlers.get_users)
    server.router.register_route("POST", "/login", handlers.login_user)

    server.bind()
    server.run()
