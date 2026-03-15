"""Simple cache abstraction with a Redis-backed implementation and an in-memory fallback.

This file intentionally keeps the API minimal so feature engineering code can
use zadd/zrangebyscore and basic setex/get operations without being coupled
to a specific backend.
"""
from typing import Any, List, Tuple, Optional
import time

try:
    import redis
except Exception:
    redis = None


class CacheBase:
    def zadd(self, key: str, score: float, member: str) -> None:
        raise NotImplementedError

    def zrangebyscore(self, key: str, min_score: float, max_score: float) -> List[Tuple[float, str]]:
        raise NotImplementedError

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        raise NotImplementedError

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def incr(self, key: str, amount: int = 1) -> int:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError


class RedisCache(CacheBase):
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        if redis is None:
            raise RuntimeError("redis library not available")
        self._client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def zadd(self, key: str, score: float, member: str) -> None:
        self._client.zadd(key, {member: score})

    def zrangebyscore(self, key: str, min_score: float, max_score: float) -> List[Tuple[float, str]]:
        # returns list of members; we stored member as a JSON or string that encodes amount
        members = self._client.zrangebyscore(key, min_score, max_score, withscores=True)
        # convert to (score, member)
        return [(float(score), member) for member, score in [(m[0], m[1]) for m in members]]

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        self._client.setex(key, ttl_seconds, value)

    def get(self, key: str) -> Optional[Any]:
        return self._client.get(key)

    def incr(self, key: str, amount: int = 1) -> int:
        return self._client.incr(key, amount)

    def delete(self, key: str) -> None:
        self._client.delete(key)


class InMemoryCache(CacheBase):
    def __init__(self):
        # for zsets: key -> list of tuples (score, member)
        self._zsets = {}
        self._kv = {}
        self._expirations = {}

    def _purge_expired(self):
        now = time.time()
        keys = [k for k, t in self._expirations.items() if t is not None and t <= now]
        for k in keys:
            self._kv.pop(k, None)
            self._expirations.pop(k, None)

    def zadd(self, key: str, score: float, member: str) -> None:
        self._zsets.setdefault(key, []).append((score, member))

    def zrangebyscore(self, key: str, min_score: float, max_score: float) -> List[Tuple[float, str]]:
        items = self._zsets.get(key, [])
        return [(s, m) for (s, m) in items if min_score <= s <= max_score]

    def setex(self, key: str, ttl_seconds: int, value: Any) -> None:
        self._kv[key] = value
        self._expirations[key] = time.time() + ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        self._purge_expired()
        return self._kv.get(key)

    def incr(self, key: str, amount: int = 1) -> int:
        self._kv[key] = int(self._kv.get(key, 0)) + amount
        return self._kv[key]

    def delete(self, key: str) -> None:
        self._kv.pop(key, None)
        self._expirations.pop(key, None)


def make_cache(cfg: dict) -> CacheBase:
    """Factory: returns RedisCache if redis lib available and config asks for redis,
    otherwise returns an in-memory fallback useful for unit tests and local dev.
    """
    driver = cfg.get("driver", "memory")
    if driver == "redis":
        if redis is None:
            raise RuntimeError("redis library not installed; cannot create RedisCache")
        return RedisCache(host=cfg.get("host", "localhost"), port=cfg.get("port", 6379), db=cfg.get("db", 0))
    return InMemoryCache()
