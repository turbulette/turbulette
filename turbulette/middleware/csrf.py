# Adapted from https://github.com/piccolo-orm/piccolo_api

from string import ascii_letters, digits
from enum import Enum
from typing import Tuple
from starlette.datastructures import URL
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    Request,
    RequestResponseEndpoint,
)
from starlette.responses import Response
from starlette.types import ASGIApp
from starlette.exceptions import HTTPException

from turbulette.conf import settings
from turbulette.utils import get_random_string
from turbulette.conf.exceptions import ImproperlyConfigured


CSRF_ALLOWED_CHARS = ascii_letters + digits
SAFE_HTTP_METHODS = ("GET", "HEAD", "OPTIONS", "TRACE")
CSRF_REQUEST_SCOPE_NAME = "csrftoken"
ONE_YEAR = 31536000  # 365 * 24 * 60 * 60
CSRF_TOKEN_LENGTH = 64


class SubmitMethod(Enum):
    """Authorized methods to use when transmitting the CSRF token."""

    HEADER = "header"
    FORM = "form"


class CSRFNotFound(HTTPException):
    pass


def get_new_token() -> str:
    return get_random_string(CSRF_TOKEN_LENGTH, ascii_letters + digits)


def is_valid_referer(request: Request) -> bool:
    header: str = request.headers.get("origin") or request.headers.get("referer") or ""

    url = URL(header)
    hostname = url.hostname
    is_valid = hostname in settings.ALLOWED_HOSTS if hostname else False
    return is_valid


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Middleware.

    For GET requests, set a random token as a cookie. For unsafe HTTP methods,
    require a HTTP header to match the cookie value, otherwise the request
    is rejected.

    This uses the Double Submit Cookie style of CSRF prevention. For more
    information:

    https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#double-submit-cookie
    https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#use-of-custom-request-headers

    This is currently only intended for use using AJAX - since the CSRF token
    needs to be added to the request header.
    """

    def __init__(
        self,
        app: ASGIApp,
        cookie_name=settings.CSRF_COOKIE_NAME,
        header_name=settings.CSRF_HEADER_NAME,
        max_age=ONE_YEAR,
        **kwargs,
    ):
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.max_age = max_age
        super().__init__(app, **kwargs)

    async def get_token_from_request(
        self, request: Request
    ) -> Tuple[str, SubmitMethod]:
        token, method = None, None

        if settings.CSRF_HEADER_PARAM:
            token = request.headers.get(self.header_name, None)
            method = SubmitMethod.HEADER
        elif settings.CSRF_FORM_PARAM:
            form_data = await request.form()
            token = form_data.get(self.cookie_name, None)
            request.scope.update({"form": form_data})
            method = SubmitMethod.FORM
        else:
            raise ImproperlyConfigured(
                "Either CSRF_HEADER_PARAM or CSRF_FORM_PARAM setting must be True"
            )

        if not token:
            raise CSRFNotFound(
                status_code=403,
                detail=f"The CSRF token was not found in {method.value}",
            )

        return token, method

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.method in SAFE_HTTP_METHODS:
            token = request.cookies.get(self.cookie_name, None)
            token_required = token is None

            if token_required:
                token = get_new_token()

            request.scope.update({CSRF_REQUEST_SCOPE_NAME: token})
            response = await call_next(request)

            if token_required and token:
                response.set_cookie(
                    self.cookie_name,
                    token,
                    max_age=self.max_age,
                )
            return response

        cookie_token = request.cookies.get(self.cookie_name)
        if not cookie_token:
            return Response("No CSRF cookie found", status_code=403)

        try:
            token, method = await self.get_token_from_request(request)
        except CSRFNotFound as error:
            return Response(error.detail, status_code=403)

        if token and (cookie_token != token):
            return Response(
                f"The CSRF token in the {method.value} doesn't match the cookie.",
                status_code=403,
            )

        # Provides defense in depth:
        if request.base_url.is_secure:
            # According to this paper, the referer header is present in
            # the vast majority of HTTPS requests, but not HTTP requests,
            # so only check it for HTTPS.
            # https://seclab.stanford.edu/websec/csrf/csrf.pdf
            if not is_valid_referer(request):
                return Response("Referrer or origin is incorrect", status_code=403)

        request.scope.update({CSRF_REQUEST_SCOPE_NAME: cookie_token})

        return await call_next(request)
