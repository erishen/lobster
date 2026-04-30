"""测试优化后的记忆存储"""

import pytest
from lobster.core.memory_store import OptimizedVectorStore, EnhancedMemoryManager


class TestOptimizedVectorStore:
    """测试优化的向量存储"""

    def test_initialization(self, tmp_path):
        """测试初始化"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        assert store.storage_path.exists()
        assert store.index == []

    def test_add_content(self, tmp_path):
        """测试添加内容"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        content_id = store.add("这是一条测试内容")

        assert content_id is not None
        assert len(store.index) == 1
        assert store.index[0]["content"] == "这是一条测试内容"

    def test_add_with_metadata(self, tmp_path):
        """测试带元数据添加"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        metadata = {"tags": ["test", "example"], "category": "demo"}
        _ = store.add("测试内容", metadata=metadata)

        assert store.index[0]["metadata"]["tags"] == ["test", "example"]
        assert store.index[0]["metadata"]["category"] == "demo"

    def test_search_keyword(self, tmp_path):
        """测试关键词搜索"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        store.add("Python 是一门编程语言")
        store.add("Java 也是编程语言")
        store.add("今天天气不错")

        results = store.search("编程", method="keyword")

        assert len(results) >= 1
        assert any("编程" in r["content"] for r in results)

    def test_search_similarity(self, tmp_path):
        """测试相似度搜索"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        store.add("machine learning is a branch of artificial intelligence")
        store.add("deep learning is a method of machine learning")
        store.add("I had lunch today")

        results = store.search("machine learning", method="similarity")

        assert len(results) >= 1

    def test_search_fuzzy(self, tmp_path):
        """测试模糊搜索"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        store.add("Python programming language")
        store.add("Java development")

        results = store.search("Pythn", method="fuzzy")

        assert len(results) >= 1

    def test_search_hybrid(self, tmp_path):
        """测试混合搜索"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        store.add("Python 是一门流行的编程语言")
        store.add("JavaScript 用于网页开发")
        store.add("Go 语言由 Google 开发")

        results = store.search_hybrid("Python 编程")

        assert len(results) >= 1

    def test_delete(self, tmp_path):
        """测试删除内容"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        content_id = store.add("要删除的内容")
        assert len(store.index) == 1

        result = store.delete(content_id)

        assert result is True
        assert len(store.index) == 0

    def test_delete_nonexistent(self, tmp_path):
        """测试删除不存在的内容"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        result = store.delete("nonexistent_id")

        assert result is False

    def test_clear(self, tmp_path):
        """测试清空内容"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        store.add("内容1")
        store.add("内容2")
        store.add("内容3")

        assert len(store.index) == 3

        store.clear()

        assert len(store.index) == 0

    def test_count(self, tmp_path):
        """测试计数"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        assert store.count() == 0

        store.add("内容1")
        store.add("内容2")

        assert store.count() == 2

    def test_get_all(self, tmp_path):
        """测试获取所有内容"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        store.add("内容1")
        store.add("内容2")

        all_content = store.get_all()

        assert len(all_content) == 2

    def test_tokenize(self, tmp_path):
        """测试分词"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        tokens = store._tokenize("Hello World Python")

        assert "hello" in tokens
        assert "world" in tokens
        assert "python" in tokens

    def test_levenshtein_distance(self, tmp_path):
        """测试编辑距离"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        distance = store._levenshtein_distance("kitten", "sitting")
        assert distance == 3

        distance = store._levenshtein_distance("", "test")
        assert distance == 4

        distance = store._levenshtein_distance("same", "same")
        assert distance == 0

    def test_fuzzy_match(self, tmp_path):
        """测试模糊匹配"""
        store = OptimizedVectorStore(storage_path=str(tmp_path / "memory"))

        assert store._fuzzy_match("python", "python", threshold=0.7) is True
        assert store._fuzzy_match("python", "pythn", threshold=0.7) is True
        assert store._fuzzy_match("python", "java", threshold=0.7) is False


class TestEnhancedMemoryManager:
    """测试增强的记忆管理器"""

    def test_initialization(self, tmp_path):
        """测试初始化"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        assert manager.store is not None

    def test_add_memory(self, tmp_path):
        """测试添加记忆"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        memory_id = manager.add_memory("这是一条记忆", tags=["test"], category="demo")

        assert memory_id is not None

    def test_search_memory(self, tmp_path):
        """测试搜索记忆"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        manager.add_memory("Python 是一门编程语言", tags=["tech"])
        manager.add_memory("今天天气不错", tags=["life"])

        results = manager.search_memory("Python", method="keyword")

        assert len(results) >= 1

    def test_search_memory_hybrid(self, tmp_path):
        """测试混合搜索记忆"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        manager.add_memory("机器学习很重要")
        manager.add_memory("深度学习是机器学习的分支")

        results = manager.search_memory("机器学习", method="hybrid")

        assert len(results) >= 1

    def test_list_memories(self, tmp_path):
        """测试列出所有记忆"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        manager.add_memory("记忆1")
        manager.add_memory("记忆2")

        memories = manager.list_memories()

        assert len(memories) == 2

    def test_delete_memory(self, tmp_path):
        """测试删除记忆"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        memory_id = manager.add_memory("要删除的记忆")
        result = manager.delete_memory(memory_id)

        assert result is True
        assert len(manager.list_memories()) == 0

    def test_clear_memories(self, tmp_path):
        """测试清空记忆"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        manager.add_memory("记忆1")
        manager.add_memory("记忆2")

        manager.clear_memories()

        assert len(manager.list_memories()) == 0

    def test_get_stats(self, tmp_path):
        """测试获取统计信息"""
        manager = EnhancedMemoryManager(storage_path=str(tmp_path / "memory"))

        manager.add_memory("记忆1", tags=["tag1"], category="cat1")
        manager.add_memory("记忆2", tags=["tag2"], category="cat1")
        manager.add_memory("记忆3", tags=["tag1"], category="cat2")

        stats = manager.get_stats()

        assert stats["total"] == 3
        assert "cat1" in stats["categories"]
        assert "tag1" in stats["tags"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
