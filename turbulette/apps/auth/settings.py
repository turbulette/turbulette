from datetime import timedelta


GRAPHQL_JWT = {
    "JWT_ALGORITHM": "HS256",
    "JWT_EXPIRE_MINUTES": 15,
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_VERIFY": True,
    "JWT_PREFIX": "JWT",
    "JWT_EXPIRATION_DELTA": timedelta(seconds=60 * 5),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    "JWT_ALLOW_REFRESH": True,
    "JWT_AUDIENCE": None,
    "JWT_ISSUER": None,
    "JWT_LEEWAY": 0,
}

SETTINGS_RULES = {
    "REQUIRED_SETTINGS": ["SECRET_KEY", "AUTH_USER_MODEL"]
}

HASH_ALGORITHM = "bcrypt"
