from inspect import getmodule
from gino.declarative import ModelType
from turbulette.conf import registry, db
from turbulette.utils.normalize import camel_to_snake


class BaseModelMeta(ModelType):
    """Metaclass for turbulette's base model class

    The metaclass auto fill the ``__tablename__`` class attribute
    using the app name from which the model class is defined,
    concatenated to the model class name.
    The naming follow snake_case convention
    """

    def __new__(cls, name, bases, namespace, **kwargs):
        rv = type.__new__(cls, name, bases, namespace)
        rv.__namespace__ = namespace
        if rv.__table__ is None:
            if not hasattr(rv, "__tablename__") and not bases[0].__class__ is ModelType:

                package = getmodule(rv).__name__.rsplit(".", maxsplit=1)[-2]
                # Generate the snake_case name using the app name and class name
                table_name = (
                    f"{registry.get_app_by_package(package).label}"
                    f"_{camel_to_snake(name)}"
                )

                rv.__tablename__ = table_name
                # Add namespace to make GINO aware of the new name
                rv.__namespace__.update({"__tablename__": table_name})
            rv.__table__ = getattr(rv, "_init_table")(rv)
        return rv


class Model(db.Model, metaclass=BaseModelMeta):
    """Base model class for gino models
    """

    def __repr__(self, key: str = None):
        if not key:
            key = getattr(self, str(self.query.primary_key[0]))
        return f"<{type(self).__name__}: {key}>"
