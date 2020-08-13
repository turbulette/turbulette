import sys
from types import ModuleType
from .exceptions import NotReadyError
from . import constants
from .utils import get_config_from_paths

registry = None
db = None
settings = None

SIMPLE_SETTINGS = {
    constants.REQUIRED_SETTINGS: set(),
    constants.REQUIRED_SETTINGS_TYPES: {},
    constants.REQUIRED_NOT_NONE_SETTINGS: set(),
    constants.SETTINGS_LOGS: False,
}


# class ConfModule(ModuleType):
#     """Manage configuration resources access
#     """

#     def __init__(self, name):
#         super(ConfModule, self).__init__(name)
#         self.simple_settings = {
#             constants.REQUIRED_SETTINGS: set(),
#             constants.REQUIRED_SETTINGS_TYPES: {},
#             constants.REQUIRED_NOT_NONE_SETTINGS: set(),
#             constants.SETTINGS_LOGS: False,
#         }
#         self.registry = None
#         self.db = None
#         self.settings = None

#     def __getattribute__(self, attr):
#         val = object.__getattribute__(self, attr)
#         # Attributes may want to be accessed before their initialization
#         if val is None:
#             raise NotReadyError(attr)
#         return val

#     # def __setattr__(self, name, value):
#     #     # Attributes can only be set once
#     #     # This guarantee that all references on any of the class attributes
#     #     # will give access to the same object, from the moment it exists
#     #     if not self.__dict__.get(name):
#     #         self.__dict__[name] = value
#     #     else:
#     #         raise ValueError(f"{name} : This attribute can only be set once")

# _conf_module = ConfModule(__name__)
# sys.modules[__name__] = _conf_module
