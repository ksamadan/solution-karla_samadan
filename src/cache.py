from fnmatch import fnmatch
from time import monotonic
from typing import Any


_cache: dict[str, tuple[float, Any]] = {}


async def get_cache(key: str) -> Any | None:
    item = _cache.get(key)

    if item is None:
        return None

    expires_at, value = item

    if monotonic() > expires_at:
        _cache.pop(key, None)
        return None

    return value


async def set_cache(
    key: str,
    value: Any,
    expire_seconds: int = 60,
) -> None:
    _cache[key] = (monotonic() + expire_seconds, value)


async def delete_cache_pattern(pattern: str) -> None:
    keys_to_delete = [
        key
        for key in _cache
        if fnmatch(key, pattern)
    ]

    for key in keys_to_delete:
        _cache.pop(key, None)
