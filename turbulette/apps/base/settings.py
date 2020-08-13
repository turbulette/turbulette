# from turbulette.conf import (
#     SIMPLE_SETTINGS
# )

# `simple_settings` need the SIMPLE_SETTINGS settings
# to process the rules
# SIMPLE_SETTINGS = simple_settings

# Base settings rules
SETTINGS_RULES = {
    "REQUIRED_SETTINGS": [
        "INSTALLED_APPS",
        "GRAPHQL_ENDPOINT",
        "DEBUG"
    ],

    "REQUIRED_SETTINGS_TYPES": {
        "APOLLO_TRACING": "bool",
        "APOLLO_FEDERATION": "bool",
        "DEBUG": "bool",
        "INSTALLED_APPS": "json.loads",
        "MIDDLEWARE_CLASSES": "json.loads",
        "GRAPHQL_ENDPOINT": "str"
    }
}

###########################
# DEFAULT SETTINGS
###########################

# Enable ariadne apollo tracing extension
APOLLO_TRACING = False


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
        "my_project": {"level": "INFO", "propagate": True,},
    },
}
