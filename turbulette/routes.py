from starlette.responses import JSONResponse
from turbulette.conf import settings
from .middleware.csrf import get_new_token


async def csrf(request):  # pylint: disable=unused-argument
    """Set the CSRF cookie and return a `JSONResponse` with the token.

    We need this REST endpoint to protect against CSRF
    because all GraphQL queries use `POST` method, so they are not safe to transmit the token.

    This function is meant to be used in the `routing` module of the Turbulette project
    to create the actual CSRF route, if you need it.
    """
    token = get_new_token()
    response = JSONResponse({"csrftoken": token})
    response.set_cookie(
        settings.CSRF_COOKIE_NAME,
        token,
        httponly=settings.CSRF_COOKIE_HTTPONLY,
        secure=settings.CSRF_COOKIE_SECURE,
    )
    return response
