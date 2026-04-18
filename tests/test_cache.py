"""测试工具缓存模块"""

import pytest
import time

from lobster.core.cache import (
    ToolCache,
    tool_cache,
    get_tool_cache,
    cached_tool,
)


class TestToolCache:
    """测试工具缓存"""

    def test_singleton(self):
        """测试单例模式"""
        cache1 = ToolCache()
        cache2 = ToolCache()
        assert cache1 is cache2

    def test_get_tool_cache(self):
        """测试获取缓存实例"""
        cache = get_tool_cache()
        assert cache is tool_cache

    def test_set_and_get(self):
        """测试设置和获取缓存"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {"param": "value"}, {"result": "success"})
        result = cache.get("test_tool", {"param": "value"})

        assert result is not None
        assert result["result"] == "success"

    def test_cache_miss(self):
        """测试缓存未命中"""
        cache = ToolCache()
        cache.clear()

        result = cache.get("nonexistent_tool", {})
        assert result is None

    def test_cache_with_different_params(self):
        """测试不同参数的缓存"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {"param": "a"}, {"result": "A"})
        cache.set("test_tool", {"param": "b"}, {"result": "B"})

        result_a = cache.get("test_tool", {"param": "a"})
        result_b = cache.get("test_tool", {"param": "b"})

        assert result_a["result"] == "A"
        assert result_b["result"] == "B"

    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {"param": "value"}, {"result": "success"}, ttl=1)

        result = cache.get("test_tool", {"param": "value"})
        assert result is not None

        time.sleep(1.5)

        result = cache.get("test_tool", {"param": "value"})
        assert result is None

    def test_cache_invalidation(self):
        """测试缓存失效"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {"param": "value"}, {"result": "success"})

        invalidated = cache.invalidate("test_tool", {"param": "value"})
        assert invalidated is True

        result = cache.get("test_tool", {"param": "value"})
        assert result is None

    def test_invalidate_nonexistent(self):
        """测试失效不存在的缓存"""
        cache = ToolCache()
        cache.clear()

        invalidated = cache.invalidate("nonexistent", {})
        assert invalidated is False

    def test_cache_clear(self):
        """测试清除缓存"""
        cache = ToolCache()
        cache.set("tool_a", {}, {"result": "A"})
        cache.set("tool_b", {}, {"result": "B"})

        cache.clear()

        assert cache.get("tool_a", {}) is None
        assert cache.get("tool_b", {}) is None

    def test_lru_eviction(self):
        """测试 LRU 淘汰"""
        cache = ToolCache()
        cache.clear()

        cache._max_size = 3
        cache.set("tool_1", {}, {"result": "1"})
        cache.set("tool_2", {}, {"result": "2"})
        cache.set("tool_3", {}, {"result": "3"})
        cache.set("tool_4", {}, {"result": "4"})

        assert cache.get("tool_1", {}) is None
        assert cache.get("tool_2", {}) is not None
        assert cache.get("tool_3", {}) is not None
        assert cache.get("tool_4", {}) is not None

        cache._max_size = 100

    def test_lru_access_order(self):
        """测试 LRU 访问顺序"""
        cache = ToolCache()
        cache.clear()

        cache._max_size = 3
        cache.set("tool_1", {}, {"result": "1"})
        cache.set("tool_2", {}, {"result": "2"})
        cache.set("tool_3", {}, {"result": "3"})

        cache.get("tool_1", {})

        cache.set("tool_4", {}, {"result": "4"})

        assert cache.get("tool_1", {}) is not None
        assert cache.get("tool_2", {}) is None
        assert cache.get("tool_3", {}) is not None
        assert cache.get("tool_4", {}) is not None

        cache._max_size = 100

    def test_get_stats(self):
        """测试获取统计"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {}, {"result": "success"})

        cache.get("test_tool", {})
        cache.get("test_tool", {})
        cache.get("nonexistent", {})

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_hit_rate(self):
        """测试命中率"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {}, {"result": "success"})

        cache.get("test_tool", {})
        cache.get("nonexistent", {})

        stats = cache.get_stats()
        assert stats["hit_rate"] == "50.0%"

    def test_cleanup_expired(self):
        """测试清理过期缓存"""
        cache = ToolCache()
        cache.clear()

        cache.set("tool_1", {}, {"result": "1"}, ttl=1)
        cache.set("tool_2", {}, {"result": "2"}, ttl=10)

        time.sleep(1.5)

        expired_count = cache.cleanup_expired()
        assert expired_count == 1

        assert cache.get("tool_1", {}) is None
        assert cache.get("tool_2", {}) is not None

    def test_get_cache_info(self):
        """测试获取缓存详情"""
        cache = ToolCache()
        cache.clear()

        cache.set("test_tool", {"param": "value"}, {"result": "success"})

        info = cache.get_cache_info()
        assert "stats" in info
        assert "items" in info
        assert len(info["items"]) == 1
        assert "key" in info["items"][0]
        assert "created_at" in info["items"][0]
        assert "expires_at" in info["items"][0]


class TestCachedToolDecorator:
    """测试缓存装饰器"""

    def test_cached_tool_decorator(self):
        """测试缓存装饰器"""
        call_count = 0

        @cached_tool(ttl=60)
        def my_tool(param):
            nonlocal call_count
            call_count += 1
            return {"result": param}

        tool_cache.clear()

        result1 = my_tool("test")
        result2 = my_tool("test")

        assert result1["result"] == "test"
        assert result2["result"] == "test"
        assert call_count == 1

    def test_cached_tool_different_params(self):
        """测试不同参数的缓存装饰器"""
        call_count = 0

        @cached_tool(ttl=60)
        def my_tool(param):
            nonlocal call_count
            call_count += 1
            return {"result": param}

        tool_cache.clear()

        result1 = my_tool("a")
        result2 = my_tool("b")

        assert result1["result"] == "a"
        assert result2["result"] == "b"
        assert call_count == 2

    def test_cached_tool_error_not_cached(self):
        """测试错误结果不被缓存"""
        call_count = 0

        @cached_tool(ttl=60)
        def my_tool(should_fail):
            nonlocal call_count
            call_count += 1
            if should_fail:
                return {"error": "Something went wrong"}
            return {"result": "success"}

        tool_cache.clear()

        result1 = my_tool(True)
        result2 = my_tool(True)

        assert "error" in result1
        assert call_count == 2
