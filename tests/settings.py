"""Standard settings with auth app and test apps enabled."""

from sqlalchemy.engine.url import URL, make_url
from starlette.datastructures import CommaSeparatedStrings, Secret

from turbulette.conf import get_config_from_paths

config = get_config_from_paths(["tests/.env.example", "../tests/.env.example"])

###########################
# TURBULETTE
###########################

GRAPHQL_ENDPOINT = config("GRAPHQL_ENDPOINT", cast=str, default="/graphql")

# List installed Turbulette apps
# that defines some GraphQL schema
INSTALLED_APPS = ["turbulette.apps.auth", "tests.app_1", "tests.app_2"]

MIDDLEWARES = config("MIDDLEWARES", cast=CommaSeparatedStrings)
CORSMiddleware = {
    "allow_origins": config("CORS_ALLOW_ORIGINS", default=["*"], cast=list)
}

DEBUG = config("DEBUG", cast=bool, default=True)
# Enable ariadne apollo tracing extension
APOLLO_FEDERATION = config("APOLLO_FEDERATION", cast=bool, default=False)

ARIADNE_EXTENSIONS = config(
    "ARIADNE_EXTENSIONS", cast=CommaSeparatedStrings, default=[]
)

###########################
# AUTH
###########################

# User model used for authentication.
AUTH_USER_MODEL = config("AUTH_USER_MODEL", cast=str)

# A valid hash algorithm that can be passed to CryptContext
# see https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html#module-passlib.hash
HASH_ALGORITHM = config("HASH_ALGORITHM", cast=str, default="bcrypt")

# Used to encode the JSON Web token
JWT_VERIFY = config("JWT_VERIFY", cast=bool, default=True)
JWT_REFRESH_ENABLED = config("JWT_REFRESH_ENABLED", cast=bool, default=True)
JWT_BLACKLIST_ENABLED = config("JWT_REFRESH_ENABLED", cast=bool, default=True)
JWT_BLACKLIST_TOKEN_CHECKS = config(
    "JWT_BLACKLIST_TOKEN_CHECKS", cast=CommaSeparatedStrings
)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="ES256")
JWT_AUDIENCE = config("JWT_AUDIENCE", cast=str, default="http://api.io/booking")
JWT_ISSUER = config("JWT_ISSUER", cast=str, default="http://api.io/auth/")

POLICY_CONFIG = config("POLICY_CONFIG", cast=str)

SECRET_KEY = {
    "kty": config("SECRET_KEY_KTY", cast=Secret),
    "d": config("SECRET_KEY_D", cast=Secret),
    "crv": config("SECRET_KEY_CRV", cast=Secret),
    "x": config("SECRET_KEY_X", cast=Secret),
    "y": config("SECRET_KEY_Y", cast=Secret),
}

ENCRYPTION_KEY = {"kty": "oct", "k": config("ENCRYPTION_KEY_K", cast=Secret)}

###########################
# DATABASE
###########################

DATABASES = {
    "backend": "turbulette.db_backend.gino.GinoConnection",
    "connection": {
        "DB_DRIVER": config("DB_DRIVER", default="postgresql"),
        "DB_HOST": config("DB_HOST", default=None),
        "DB_PORT": config("DB_PORT", cast=int, default=None),
        "DB_USER": config("DB_USER", default=None),
        "DB_PASSWORD": config("DB_PASSWORD", cast=Secret, default=None),
        "DB_DATABASE": config("DB_DATABASE", default=None),
    },
    "settings": {
        "DB_POOL_MIN_SIZE": config("DB_POOL_MIN_SIZE", cast=int, default=1),
        "DB_POOL_MAX_SIZE": config("DB_POOL_MAX_SIZE", cast=int, default=16),
        "DB_ECHO": config("DB_ECHO", cast=bool, default=False),
        "DB_SSL": config("DB_SSL", default=None),
        "DB_USE_CONNECTION_FOR_REQUEST": config(
            "DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True
        ),
        "DB_RETRY_LIMIT": config("DB_RETRY_LIMIT", cast=int, default=1),
        "DB_RETRY_INTERVAL": config("DB_RETRY_INTERVAL", cast=int, default=1),
    },
}
