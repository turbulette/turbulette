
class PermissionGroupNotFound(Exception):
    default_message = None

    def __init__(self, message=None):
        if message is None:
            message = self.default_message

        super().__init__(message)


class JSONWebTokenError(Exception):
    default_message = "An error occured while processing the JSON web token"

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        self.message = message
        super().__init__(message)


class InvalidJWTError(JSONWebTokenError):
    default_message = "Token is expired and/or invalid"



class InvalidJWTSignatureError(JSONWebTokenError):
    default_message = "JWT signature is invalid"



class UserDoesNotExists(Exception):
    pass
