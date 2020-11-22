from sqlalchemy.engine.url import URL, make_url
from starlette.datastructures import Secret, CommaSeparatedStrings
from turbulette.conf import get_config_from_paths

config = get_config_from_paths(["{{ project }}/.env", ".env"])

###########################
# TURBULETTE
###########################

GRAPHQL_ENDPOINT = config("GRAPHQL_ENDPOINT", cast=str, default="/graphql")

# List installed Turbulette apps
# that defines some GraphQL schema
INSTALLED_APPS = config("INSTALLED_APPS", cast=CommaSeparatedStrings, default=[])

MIDDLEWARES = config("MIDDLEWARES", cast=CommaSeparatedStrings, default=[])

CONFIGURE_LOGGING = config("CONFIGURE_LOGGING", cast=bool, default=False)
DEBUG = config("DEBUG", cast=bool, default=True)

###########################
# AUTH
###########################

SECRET_KEY = {
    "kty": config("SECRET_KEY_KTY", cast=Secret),
    "d": config("SECRET_KEY_D", cast=Secret),
    "crv": config("SECRET_KEY_CRV", cast=Secret),
    "x": config("SECRET_KEY_X", cast=Secret),
    "y": config("SECRET_KEY_Y", cast=Secret),
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
