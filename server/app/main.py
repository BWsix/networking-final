from app import handlers, logger, handlers, middlewares, framework


if __name__ == "__main__":
    server = framework.Server(logger=logger.framework)

    # global middleware that prevents CORS issues
    server.router.register_middleware(middlewares.say_ok_to_preflight_requests)

    # public routes
    server.router.register_route("POST", "/user", handlers.create_user)
    server.router.register_route("POST", "/login", handlers.login_user)

    # protected routes
    server.router.register_middleware(middlewares.inject_user)
    server.router.register_route("GET", "/me", handlers.get_me)

    # mail routes
    server.router.register_route("GET", "/mails", handlers.get_mails)
    server.router.register_route("POST", "/mail", handlers.send_mail)

    server.bind()
    server.run()
