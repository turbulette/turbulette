from inspect import getmodule
from gino.declarative import ModelType
from turbulette.conf import registry, db
from ariadne.utils import convert_camel_case_to_snake


class BaseModelMeta(ModelType):
    """Metaclass for turbulette's base model class.

    The metaclass auto fill the ``__tablename__`` class attribute
    using the app name from which the model class is defined,
    concatenated to the model class name.
    The naming follow snake_case convention
    """

    def __new__(
        cls, name, bases, namespace, **kwargs
    ):  # pylint: disable=unused-argument
        model = type.__new__(cls, name, bases, namespace)
        model.__namespace__ = namespace
        if model.__table__ is None:
            if (
                not hasattr(model, "__tablename__")
                and not bases[0].__class__ is ModelType
            ):

                package = getmodule(model).__name__.rsplit(".", maxsplit=1)[-2]
                # Generate the snake_case name using the app name and class name
                table_name = get_tablename(package, name)

                model.__tablename__ = table_name
                # Add namespace to make GINO aware of the new name
                model.__namespace__.update({"__tablename__": table_name})
            model.__table__ = getattr(model, "_init_table")(model)
        return model


class Model(db.Model, metaclass=BaseModelMeta):  # type: ignore
    """Base model class for gino models."""

    def __repr__(self, key: str = None):
        """Base repr for models.

        The output follow the standard : <class_name>: <unique key>
        The goal of the __repr__ method is to be unambiguous,
        hence the use of primary key here. This should be overridden if
        the model has a more readable attribute to help identify it
        """
        if not key:
            key = getattr(self, str(self.query.primary_key[0]))
        return f"<{type(self).__name__}: {key}>"


def get_tablename(package: str, name: str) -> str:
    """Generate a camel case table name.

    Args:
        package (str): Model's package
        name (str): Model name (usually the class name)

    Returns:
        str: The camel case table name
    """
    return (
        f"{registry.get_app_by_package(package).label}"
        f"_{convert_camel_case_to_snake(name)}"
    )
