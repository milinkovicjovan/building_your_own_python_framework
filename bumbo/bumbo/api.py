# bumbo/api.py

import os
import inspect

from parse import parse
from webob import Request
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise

from .response import Response
from .middleware import Middleware


class API:
    def __init__(self, templates_dir="templates", static_dir="static"):
        print("__init__")
        self.routes = {}

        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )

        self.exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        print("__call__")
        path_info = environ["PATH_INFO"]

        if path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static"):]
            return self.whitenoise(environ, start_response)

        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        print("wsgi_app")
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def add_route(self, path, handler, allowed_methods=None):
        print("add_route")
        assert path not in self.routes, "Such route already exists."

        if allowed_methods is None:
            allowed_methods = ["get", "post",
                               "put", "patch", "delete", "options"]

        self.routes[path] = {"handler": handler,
                             "allowed_methods": allowed_methods}

    def route(self, path, allowed_methods=None):
        print("route")

        def wrapper(handler):
            self.add_route(path, handler, allowed_methods)
            return handler

        return wrapper

    def default_response(self, response):
        print("default_response")
        response.status_code = 404
        response.text = "Not found."

    def find_handler(self, request_path):
        print("find_handler")
        for path, handler_data in self.routes.items():
            # print(path)
            parse_result = parse(path, request_path)
            # print(request_path)
            # print(parse_result.named)
            if parse_result is not None:
                return handler_data, parse_result.named

        return None, None

    def handle_request(self, request):
        print("handle_request")
        response = Response()

        handler_data, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler_data is not None:
                handler = handler_data["handler"]
                allowed_methods = handler_data["allowed_methods"]
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError(
                            "Method not allowed", request.method)
                else:
                    if request.method.lower() not in allowed_methods:
                        raise AttributeError(
                            "Method not allowed", request.method)

                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    def test_session(self, base_url="http://testserver"):
        print("test_session")
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def template(self, template_name, context=None):
        print("template")
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context)

    def add_exception_handler(self, exception_handler):
        print("add_exception_handler")
        self.exception_handler = exception_handler

    def add_middleware(self, middleware_cls):
        print("add_middleware")
        self.middleware.add(middleware_cls)
