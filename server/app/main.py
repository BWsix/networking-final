from framework import framework

if __name__ == "__main__":
    server = framework.Server()
    server.register_debug_route()
    server.bind()
    server.run()
