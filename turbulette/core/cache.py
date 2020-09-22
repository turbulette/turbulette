from caches import Cache as AsyncCache
from turbulette.core.utils import LazyInitMixin


class LazyCache(LazyInitMixin, AsyncCache):
    def __init__(self):
        super().__init__("cache")


cache = LazyCache()
