# bumbo/response.py

import json

from webob import Response as WebObResponse


class Response:
    def __init__(self):
        print("Response __init__")
        self.json = None
        self.html = None
        self.text = None
        self.content_type = None
        self.body = b""
        self.status_code = 200

    def __call__(self, environ, start_response):
        print("Response __call__")
        self.set_body_and_content_type()

        response = WebObResponse(
            body=self.body, content_type=self.content_type, status=self.status_code
        )
        return response(environ, start_response)

    def set_body_and_content_type(self):
        print("Response set_body_and_content_type")
        if self.json is not None:
            self.body = json.dumps(self.json).encode("UTF-8")
            self.content_type = "application/json"

        if self.html is not None:
            self.body = self.html.encode()
            self.content_type = "text/html"

        if self.text is not None:
            self.body = self.text
            self.content_type = "text/plain"
