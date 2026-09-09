"""Bound request bytes before multipart/JSON parsing, even without a length header."""
from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    def __init__(self, app, json_limit=1024 * 1024, upload_limit=11 * 1024 * 1024):
        self.app = app
        self.json_limit = json_limit
        self.upload_limit = upload_limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = scope.get("headers", [])
        lengths = [v for k, v in headers if k.lower() == b"content-length"]
        content_type = next((v.lower() for k, v in headers if k.lower() == b"content-type"), b"")
        limit = self.upload_limit if content_type.startswith(b"multipart/form-data;") else self.json_limit
        if len(lengths) > 1 or (lengths and (not lengths[0].isdigit() or len(lengths[0]) > 20)):
            return await JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)(scope, receive, send)
        if lengths and int(lengths[0]) > limit:
            return await JSONResponse({"detail": "Request body too large"}, status_code=413)(scope, receive, send)
        body = bytearray()
        size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            size += len(message.get("body", b""))
            if size > limit:
                return await JSONResponse({"detail": "Request body too large"}, status_code=413)(scope, receive, send)
            body.extend(message.get("body", b""))
            if not message.get("more_body", False):
                break
        if lengths and size != int(lengths[0]):
            return await JSONResponse({"detail": "Content-Length does not match body"}, status_code=400)(scope, receive, send)
        consumed = False

        async def replay():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)
