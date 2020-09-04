from turbulette.core.errors import ErrorCode, BaseError


class JWTDecodeError(BaseError):
    error_code = ErrorCode.JWT_INVALID


class JWTInvalidSignature(BaseError):
    error_code = ErrorCode.JWT_INVALID_SINATURE


class JWTExpired(BaseError):
    error_code = ErrorCode.JWT_EXPIRED


class JWTNoUsername(BaseError):
    error_code = ErrorCode.JWT_USERNAME_NOT_FOUND


class JWTInvalidPrefix(BaseError):
    error_code = ErrorCode.JWT_INVALID_PREFIX


class JWTNotFound(BaseError):
    error_code = ErrorCode.JWT_NOT_FOUND


class JWTNotFresh(BaseError):
    error_code = ErrorCode.JWT_NOT_FRESH


class JWTInvalidTokenType(BaseError):
    error_code = ErrorCode.JWT_INVALID_TOKEN_TYPE


class UserDoesNotExists(Exception):
    pass
