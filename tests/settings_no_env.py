"""Settings that doesn't source any en file."""

from sqlalchemy.engine.url import URL

###########################
# TURBULETTE
###########################

GRAPHQL_ENDPOINT = "/graphql"

# List installed Turbulette apps
# that defines some GraphQL schema
INSTALLED_APPS = ["turbulette.apps.auth", "tests.app_1", "tests.app_2"]

MIDDLEWARES = [
    "turbulette.middleware.csrf.CSRFMiddleware",
    "starlette.middleware.cors.CORSMiddleware",
]
CORSMiddleware = {"allow_origins": ["*"]}

DEBUG = True
# Enable ariadne apollo tracing extension
APOLLO_FEDERATION = False

ARIADNE_EXTENSIONS = ["ariadne.contrib.tracing.apollotracing.ApolloTracingExtension"]

###########################
# AUTH
###########################

# User model used for authentication.
AUTH_USER_MODEL = "tests.app_1.models.BaseUser"

# A valid hash algorithm that can be passed to CryptContext
# see https://passlib.readthedocs.io/en/stable/lib/passlib.hash.html#module-passlib.hash
HASH_ALGORITHM = "bcrypt"

# Used to encode the JSON Web token
JWT_VERIFY = True
JWT_REFRESH_ENABLED = True
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JWT_ALGORITHM = "ES256"
JWT_AUDIENCE = "http://api.io/booking"
JWT_ISSUER = "http://api.io/auth/"

POLICY_CONFIG = "tests/policies.json"

SECRET_KEY = {
    "kty": "EC",
    "d": "RXZ7nMEJ83eyRPmu7rjNYxgOeGH1Th7O3PvQhvfLQLw",
    "crv": "P-256",
    "x": "bZOtOYAveZdxSpiJHeCILO3IUuHIWdb29v_6y6p8I8M",
    "y": "j3N2iYJWeqvPKLTkHhlHoBLSXisO4Umc8634kS2TFSU",
}

ENCRYPTION_KEY = {"kty": "oct", "k": "iRBGS_lqSiPH_jRLt7jQPzMNzpnQGfL2Ac3tc20ou8o"}

###########################
# DATABASE
###########################

# DB connection
DATABASE_CONNECTION = {
    "DB_DRIVER": "postgresql",
    "DB_HOST": "localhost",
    "DB_PORT": 5432,
    "DB_USER": "postgres",
    "DB_PASSWORD": "",
    "DB_DATABASE": "test",
}

# DB settings
DATABASE_SETTINGS = {
    "DB_POOL_MIN_SIZE": 1,
    "DB_POOL_MAX_SIZE": 16,
    "DB_ECHO": False,
    "DB_SSL": None,
    "DB_USE_CONNECTION_FOR_REQUEST": True,
    "DB_RETRY_LIMIT": 1,
    "DB_RETRY_INTERVAL": 1,
}

DB_DSN = URL(
    drivername=DATABASE_CONNECTION["DB_DRIVER"],
    username=DATABASE_CONNECTION["DB_USER"],
    password=DATABASE_CONNECTION["DB_PASSWORD"],
    host=DATABASE_CONNECTION["DB_HOST"],
    port=DATABASE_CONNECTION["DB_PORT"],
    database=DATABASE_CONNECTION["DB_DATABASE"],
)
