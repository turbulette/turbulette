from random import SystemRandom
from typing import Any, Optional, Type

from ariadne.types import GraphQLResolveInfo

from .exceptions import NotReady


def get_random_string(size: int, allowed_chars: str):
    """Generate a cryptographically random string.

    From this answer :
    https://stackoverflow.com/a/23728630/10735573

    Args:
        size (int): string length

    Returns:
        (string): The random string
    """
    return "".join(SystemRandom().choice(allowed_chars) for _ in range(size))


def is_query(info: GraphQLResolveInfo) -> bool:
    root_names = []
    for type_ in [
        info.schema.query_type,
        info.schema.mutation_type,
        info.schema.subscription_type,
    ]:
        if type_:
            root_names.append(type_.name)
    return info.parent_type.name in root_names


class LazyInitMixin:
    """Generic wrapper to delay an object instantiation.

    Usage :

        class Foo(LazyInitMixin, WrappedClass):
            pass

        bar = Foo()

    This mixin must be placed first in the MRO, so the
    `__init__` from `LazyInitMixin` is called when instantiating Foo

    This has the advantage of conserving typing, because `bar` is an
    instance of `Foo`
    """

    lazy_attributes = frozenset(
        ("obj", "name", "__initialized__", "initialized", "__setup__")
    )

    def __init__(self, name: str):
        """Initialize a Lazy instance.

        Args:
            name (str): Name of the wrapped object.
                Only used to provide a meaningful message if `NotReady` is raised
        """
        self.obj: Optional[Type] = None
        self.name = name
        self.__initialized__ = False

    def __getattribute__(self, name: str) -> Any:
        """Proxy that delegates attribute accesses to the wrapped object after initialization."""
        # Don't delegate when accessing `LazyInitMixin` attributes
        if name in object.__getattribute__(self, "lazy_attributes"):
            return object.__getattribute__(self, name)
        if not self.__initialized__:
            raise NotReady(f"{self.name} is not ready yet")
        return object.__getattribute__(self.obj, name)

    def __setup__(self, obj: Any):
        """Actually initialize the wrapped object."""
        self.__initialized__ = True
        self.obj = obj

    @property
    def initialized(self) -> bool:
        return self.__initialized__
