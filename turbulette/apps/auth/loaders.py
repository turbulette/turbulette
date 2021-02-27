from typing import Any, Dict, List, Optional, Sequence

from aiodataloader import DataLoader

from turbulette.type import GraphQLContext, LoaderFunction


def parse_db_id(value: Any) -> Optional[int]:
    try:
        value = int(value)
        if value > 0:
            return value
        return None
    except (TypeError, ValueError):
        return None


def get_loader_context_key(name: str) -> str:
    return f"__loader_{name}"


def get_loader(
    context: GraphQLContext,
    name: str,
    loader_function: LoaderFunction,
    *,
    coerce_id_to=parse_db_id,
) -> DataLoader:
    context_key = get_loader_context_key(name)
    if context_key not in context:
        wrapped_loader_function = wrap_loader_function(loader_function, coerce_id_to)
        context[context_key] = DataLoader(wrapped_loader_function, get_cache_key=str)
    return context[context_key]


def wrap_loader_function(
    loader_function: LoaderFunction, coerce_id=parse_db_id
) -> LoaderFunction:
    async def wrapped_loader_function(ids: Sequence[Any]) -> List[Any]:
        data: Dict[str, Any] = {}
        graphql_ids = [str(i) for i in ids]
        internal_ids: List[Any] = []

        for graphql_id in graphql_ids:
            internal_id = coerce_id(graphql_id)
            if internal_id is not None:
                internal_ids.append(internal_id)
            else:
                data[graphql_id] = None
        if internal_ids:
            for item in await loader_function(internal_ids):
                data[str(item.id)] = item
        return [data.get(i) for i in graphql_ids]

    return wrapped_loader_function


class AuthDataloader(DataLoader):
    pass


###########################################################
# From spectrum
###########################################################


class AriadneDataLoader(DataLoader):
    context_key: Optional[str] = None

    def __init__(self, *args, context, **kwargs):
        self.context = context
        super().__init__(*args, **kwargs)

    @classmethod
    def for_context(cls, context: Dict):
        key = cls.context_key
        if key is None:
            raise TypeError("Data loader %r does not define a context key" % (cls,))
        loaders = context.setdefault("loaders", {})
        if key not in loaders:
            user = user_from_context(context)
            loaders[key] = cls(context=context)
        loader = loaders[key]
        assert isinstance(loader, cls)
        return loader


class BookLoader(AriadneDataLoader):
    context_key = "books"

    async def batch_load_fn(self, keys):
        pass


async def book_resolver(obj, info, book_id):
    loader = BookLoader.for_context(info.context)
    book = await loader.load(book_id)
    ...  # your logic here
