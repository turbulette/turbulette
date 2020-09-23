from datetime import timedelta


SETTINGS_RULES = {
    "REQUIRED_SETTINGS": ["AUTH_USER_MODEL", "SECRET_KEY"],
    "REQUIRED_SETTINGS_TYPES": {
        "JWT_ALGORITHM": "str",
        "JWT_AUDIENCE": "str",
        "JWT_ISSUER": "str",
        "JWT_PREFIX": "str",
        "JWT_VERIFY": "bool",
        "JWT_JTI_SIZE": "int",
        "JWT_VERIFY_EXPIRATION": "bool",
        "JWT_REFRESH_ENABLED": "bool",
        "JWT_BLACKLIST_ENABLED": "bool",
    },
}

HASH_ALGORITHM = "bcrypt"

# JWT
JWT_VERIFY = True
JWT_VERIFY_EXPIRATION = True
JWT_PREFIX = "JWT"
JWT_EXPIRATION_DELTA = timedelta(seconds=60 * 5)
JWT_REFRESH_EXPIRATION_DELTA = timedelta(days=7)
JWT_FRESH_DELTA = timedelta(seconds=15)
JWT_REFRESH_ENABLED = True
JWT_AUDIENCE = None
JWT_ISSUER = None
JWT_LEEWAY = timedelta(0)
JWT_BLACKLIST_ENABLED = False
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JWT_JTI_SIZE = 16

JWT_ALGORITHM = "ES256"

JWT_ENCRYPT = False
JWE_ALGORITHM = "A256KW"
JWE_ENCRYPTION = "A256CBC-HS512"

AUTH_USER_MODEL_TABLENAME = None

# JWT_ACCESS_LOCATION = "headers"
# JWT_REFRESH_LOCATION = "headers"
# JWT_ACCESS_COOKIE_NAME = "access_token"
# JWT_REFRESH_COOKIE_NAME = "refresh_token"
