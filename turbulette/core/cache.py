from caches import Cache as AsyncCache
from turbulette.core.utils import LazyInitMixin


class LazyCache(LazyInitMixin, AsyncCache):
    pass


cache = LazyCache("cache")
