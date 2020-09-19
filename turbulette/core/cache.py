from typing import Any
from caches import Cache
from turbulette.conf import settings

cache = Cache(settings.QUERY_CACHE)
