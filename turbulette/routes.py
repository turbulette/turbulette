from starlette.responses import JSONResponse
from turbulette.conf import settings
from .middleware.csrf import get_new_token


async def csrf(request):
    token = get_new_token()
    response = JSONResponse({"csrftoken": token})
    response.set_cookie(
        settings.CSRF_COOKIE_NAME,
        token,
        httponly=settings.CSRF_COOKIE_HTTPONLY,
        secure=settings.CSRF_COOKIE_SECURE,
    )
    return response
