# bumbo/middleware.py

from webob import Request


class Middleware:
    def __init__(self, app):
        print("Middleware __init__")
        print("----" * 25)
        self.app = app

    def __call__(self, environ, start_response):
        print("Middleware __init__")
        request = Request(environ)
        response = self.app.handle_request(request)
        return response(environ, start_response)

    def add(self, middleware_cls):
        print("Middleware add")
        self.app = middleware_cls(self.app)

    def process_request(self, req):
        pass

    def process_response(self, req, resp):
        pass

    def handle_request(self, request):
        print("Middleware handle_request")
        self.process_request(request)
        response = self.app.handle_request(request)
        self.process_response(request, response)

        return response
