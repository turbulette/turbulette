class JWTDecodeError(Exception):
    default_message = "An error occured while processing the JSON web token"

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        self.message = message
        super().__init__(message)


class JWTInvalidSignatureError(JWTDecodeError):
    default_message = "JWT signature cannot be validated"


class JWTExpiredError(JWTDecodeError):
    default_message = "JWT has exprired"


class UserDoesNotExists(Exception):
    pass
