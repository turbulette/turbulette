OVERRIDE_BY_ENV = True

# Base settings rules
SETTINGS_RULES = {
    "REQUIRED_SETTINGS": ["INSTALLED_APPS", "GRAPHQL_ENDPOINT", "DEBUG"],
    "REQUIRED_SETTINGS_TYPES": {
        "APOLLO_TRACING": "bool",
        "APOLLO_FEDERATION": "bool",
        "DEBUG": "bool",
        "MIDDLEWARE_CLASSES": "json.loads",
        "GRAPHQL_ENDPOINT": "str",
        "CSRF_COOKIE_NAME": "str",
        "CSRF_HEADER_NAME": "str",
        "CSRF_COOKIE_HTTPONLY": "bool",
        "CSRF_COOKIE_SECURE": "bool",
        "CSRF_FORM_PARAM": "bool",
        "CSRF_HEADER_PARAM": "bool",
        "ALLOWED_HOSTS": "json.loads",
    },
    "OVERRIDE_BY_ENV": OVERRIDE_BY_ENV,
}

###########################
# DEFAULT SETTINGS
###########################

ARIADNE_EXTENSIONS: list = []


# Tell ariadne to create schema with federation support
# see https://ariadnegraphql.org/docs/apollo-federation#federated-architecture-example
APOLLO_FEDERATION = False


GRAPHQL_ENDPOINT = "/graphql/"

# Logging settings to use when `CONFIGURE_LOGGING` is True.
# see https://github.com/drgarcia1986/simple-settings#configure-logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "logfile": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "turbulette.log",
            "maxBytes": 50 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "default",
        },
    },
    "loggers": {
        "": {"handlers": ["logfile"], "level": "ERROR"},
        "turbulette": {
            "level": "INFO",
            "propagate": True,
        },
    },
}

CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "X-CSRFToken"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
CSRF_HEADER_PARAM = True

# Require python-multipart
CSRF_FORM_PARAM = False

ALLOWED_HOSTS: list = []

CONFIGURE_LOGGING = False

CACHE = "locmem://null"

ERROR_FIELD = "errors"
