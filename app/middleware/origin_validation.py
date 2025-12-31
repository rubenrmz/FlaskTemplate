# app/middleware/origin_validation.py
from werkzeug.wrappers import Request, Response

class RequireOriginMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        
        if request.headers.get("Origin") is None:
            response = Response("No autorizado", status=403)
            return response(environ, start_response)

        return self.app(environ, start_response)