from datetime import timedelta


SETTINGS_RULES = {
    "REQUIRED_SETTINGS": ["AUTH_USER_MODEL", "JWK_KTY"],
    "REQUIRED_SETTINGS_TYPES": {
        "JWT_ALGORITHM": "str",
        "JWK_KTY": "str",
        "JWK_EC_PARAMS": "json.loads",
        "JWK_RSA_PARAMS": "json.loads",
        "JWK_OKP_PARAMS": "json.loads",
        "JWK_OCT_PARAMS": "json.loads",
        "JWT_AUDIENCE": "str",
        "JWT_ISSUER": "str",
        "JWT_PREFIX": "str",
        "JWT_VERIFY": "bool",
        "JWT_JTI_SIZE": "int",
        "JWT_VERIFY_EXPIRATION": "bool",
        "JWT_REFRESH_ENABLED": "bool",
        "JWT_BLACKLIST_ENABLED": "bool",
        "JWT_BLACKLIST_TOKEN_CHECKS": "json.loads"
    },
}

HASH_ALGORITHM = "bcrypt"

# JWT
JWT_VERIFY = True
JWT_VERIFY_EXPIRATION = True
JWT_PREFIX = "JWT"
JWT_EXPIRATION_DELTA = timedelta(seconds=60 * 5)
JWT_REFRESH_EXPIRATION_DELTA = timedelta(days=7)
JWT_REFRESH_ENABLED = True
JWT_AUDIENCE = None
JWT_ISSUER = None
JWT_LEEWAY = timedelta(0)
JWT_BLACKLIST_ENABLED = False
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JWT_JTI_SIZE = 16

JWT_ALGORITHM = "ES256"

# Must be one of (EC, RSA, OKP, oct)
JWK_KTY = "EC"

JWK_EC_PARAMS = {"crv": "P-256"}
JWK_RSA_PARAMS = {"size": 2048}
JWK_OKP_PARAMS = {"crv": "Ed25519"}
JWK_oct_PARAMS = {"size": 256}

# JWT_ACCESS_LOCATION = "headers"
# JWT_REFRESH_LOCATION = "headers"
# JWT_ACCESS_COOKIE_NAME = "access_token"
# JWT_REFRESH_COOKIE_NAME = "refresh_token"
