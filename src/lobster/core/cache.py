"""工具调用缓存模块

缓存工具调用结果，避免重复计算
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from typing import Dict, Any, Optional, Tuple


class ToolCache:
    """工具调用缓存

    使用 LRU 策略管理缓存
    """

    _instance: Optional["ToolCache"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        max_size: int = 100,
        default_ttl: int = 300,
    ):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._cache: OrderedDict[str, Tuple[Any, float, float]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def _generate_key(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """生成缓存键"""
        sorted_kwargs = json.dumps(kwargs, sort_keys=True, default=str)
        kwargs_hash = hashlib.md5(sorted_kwargs.encode()).hexdigest()[:8]
        return f"{tool_name}:{kwargs_hash}"

    def get(self, tool_name: str, kwargs: Dict[str, Any]) -> Optional[Any]:
        """获取缓存结果"""
        key = self._generate_key(tool_name, kwargs)

        if key in self._cache:
            result, expire_time, _ = self._cache[key]

            if time.time() < expire_time:
                self._cache.move_to_end(key)
                self._hits += 1
                return result
            else:
                del self._cache[key]

        self._misses += 1
        return None

    def set(
        self,
        tool_name: str,
        kwargs: Dict[str, Any],
        result: Any,
        ttl: Optional[int] = None,
    ):
        """设置缓存结果"""
        key = self._generate_key(tool_name, kwargs)
        expire_time = time.time() + (ttl or self._default_ttl)

        if key in self._cache:
            del self._cache[key]

        self._cache[key] = (result, expire_time, time.time())

        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def invalidate(self, tool_name: str, kwargs: Dict[str, Any]) -> bool:
        """使缓存失效"""
        key = self._generate_key(tool_name, kwargs)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self):
        """清除所有缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expire_time, _) in self._cache.items() if current_time >= expire_time
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "total_requests": total_requests,
        }

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存详细信息"""
        current_time = time.time()
        items = []
        for key, (result, expire_time, created_time) in self._cache.items():
            items.append(
                {
                    "key": key,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_time)),
                    "expires_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expire_time)),
                    "is_expired": current_time >= expire_time,
                    "ttl_remaining": max(0, expire_time - current_time),
                }
            )
        return {
            "stats": self.get_stats(),
            "items": items,
        }


tool_cache = ToolCache()


def get_tool_cache() -> ToolCache:
    """获取工具缓存实例"""
    return tool_cache


def cached_tool(ttl: Optional[int] = None):
    """工具缓存装饰器

    用法:
        @cached_tool(ttl=60)
        def my_tool(param1, param2):
            ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            tool_name = func.__name__
            cache_kwargs = {"args": args, **kwargs}

            cached_result = tool_cache.get(tool_name, cache_kwargs)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)

            if isinstance(result, dict) and "error" not in result:
                tool_cache.set(tool_name, cache_kwargs, result, ttl)

            return result

        return wrapper

    return decorator
