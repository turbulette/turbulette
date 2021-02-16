"""Additional REST routes."""

from starlette.responses import JSONResponse
from starlette.routing import Route

from turbulette.routes import csrf


async def welcome(request):  # pylint: disable=unused-argument
    return JSONResponse({"welcome": "welcome to the library"})


routes = [
    Route("/csrf", endpoint=csrf),
    Route("/welcome", endpoint=welcome, methods=["GET", "POST"]),
]
