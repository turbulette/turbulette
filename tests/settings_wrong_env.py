from sqlalchemy.engine.url import URL, make_url
from starlette.datastructures import Secret
from turbulette.conf.utils import get_config_from_paths

config = get_config_from_paths([".wrong", "../.wrong"])

###########################
# TURBULETTE
###########################

GRAPHQL_ENDPOINT = "/graphql"

# List installed Turbulette apps
# that defines some GraphQL schema
INSTALLED_APPS = ["turbulette.apps.auth", "tests.app_1", "tests.app_2"]

CONFIGURE_LOGGING = False

DEBUG = True

# Enable ariadne apollo tracing extension
APOLLO_TRACING = False

APOLLO_FEDERATION = False


###########################
# AUTH
###########################

# User model used for authentication.
AUTH_USER_MODEL = "tests.app_1.models.BaseUser"

# A valid hash algorithm that can be passed to CryptContext
# see https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html#module-passlib.hash
HASH_ALGORITHM = "bcrypt"


# Used to encode the JSON Web token

JWT_REFRESH_ENABLED = True
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JWT_ALGORITHM = "ES256"
JWT_AUDIENCE = "http://api.io/booking"
JWT_ISSUER = "http://api.io/auth/"

SECRET_KEY = {
    "kty": "EC",
    "d": "RXZ7nMEJ83eyRPmu7rjNYxgOeGH1Th7O3PvQhvfLQLw",
    "crv": "P-256",
    "x": "bZOtOYAveZdxSpiJHeCILO3IUuHIWdb29v_6y6p8I8M",
    "y": "j3N2iYJWeqvPKLTkHhlHoBLSXisO4Umc8634kS2TFSU",
}

###########################
# DATABASE
###########################

# DB connection
DATABASE_CONNECTION = {
    "DB_DRIVER": config("DB_DRIVER", default="postgresql"),
    "DB_HOST": config("DB_HOST", default=None),
    "DB_PORT": config("DB_PORT", cast=int, default=None),
    "DB_USER": config("DB_USER", default=None),
    "DB_PASSWORD": config("DB_PASSWORD", cast=Secret, default=None),
    "DB_DATABASE": config("DB_DATABASE", default=None),
}

# DB settings
DATABASE_SETTINGS = {
    "DB_POOL_MIN_SIZE": config("DB_POOL_MIN_SIZE", cast=int, default=1),
    "DB_POOL_MAX_SIZE": config("DB_POOL_MAX_SIZE", cast=int, default=16),
    "DB_ECHO": config("DB_ECHO", cast=bool, default=False),
    "DB_SSL": config("DB_SSL", default=None),
    "DB_USE_CONNECTION_FOR_REQUEST": config(
        "DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True
    ),
    "DB_RETRY_LIMIT": config("DB_RETRY_LIMIT", cast=int, default=1),
    "DB_RETRY_INTERVAL": config("DB_RETRY_INTERVAL", cast=int, default=1),
}

DB_DSN = config(
    "DB_DSN",
    cast=make_url,
    default=URL(
        drivername=DATABASE_CONNECTION["DB_DRIVER"],
        username=DATABASE_CONNECTION["DB_USER"],
        password=DATABASE_CONNECTION["DB_PASSWORD"],
        host=DATABASE_CONNECTION["DB_HOST"],
        port=DATABASE_CONNECTION["DB_PORT"],
        database=DATABASE_CONNECTION["DB_DATABASE"],
    ),
)
