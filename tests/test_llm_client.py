"""测试 LLM 客户端功能"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from lobster.core.llm_client import (
    ConversationManager,
    ResponseCache,
    EnhancedLLMClient,
    get_llm_client,
)


class TestConversationManager:
    """测试对话管理器"""

    def test_initialization(self):
        """测试初始化"""
        manager = ConversationManager()
        assert len(manager.history) == 0
        assert manager.max_history == 10

    def test_add_message(self):
        """测试添加消息"""
        manager = ConversationManager()
        manager.add_message("user", "你好")
        manager.add_message("assistant", "你好！")

        assert len(manager.history) == 2
        assert manager.history[0]["role"] == "user"
        assert manager.history[0]["content"] == "你好"

    def test_max_history_limit(self):
        """测试历史记录限制"""
        manager = ConversationManager(max_history=2)

        # 添加超过限制的消息
        for i in range(5):
            manager.add_message("user", f"消息{i}")
            manager.add_message("assistant", f"回复{i}")

        # 应该保留最近的对话
        assert len(manager.history) <= manager.max_history * 2

    def test_clear(self):
        """测试清空历史"""
        manager = ConversationManager()
        manager.add_message("user", "测试")
        manager.clear()

        assert len(manager.history) == 0

    def test_get_last_n_messages(self):
        """测试获取最后 n 条消息"""
        manager = ConversationManager()
        manager.add_message("user", "消息1")
        manager.add_message("assistant", "回复1")
        manager.add_message("user", "消息2")

        last_messages = manager.get_last_n_messages(2)
        assert len(last_messages) == 2

    def test_export_import_history(self):
        """测试导出导入历史"""
        manager = ConversationManager()
        manager.add_message("user", "测试")

        # 导出
        history_json = manager.export_history()
        assert "测试" in history_json

        # 导入
        new_manager = ConversationManager()
        new_manager.import_history(history_json)
        assert len(new_manager.history) == 1


class TestResponseCache:
    """测试响应缓存"""

    def test_initialization(self, tmp_path):
        """测试初始化"""
        cache = ResponseCache(cache_dir=str(tmp_path / "cache"))
        assert cache.cache_dir.exists()
        assert cache.ttl == 3600

    def test_set_and_get(self, tmp_path):
        """测试设置和获取缓存"""
        cache = ResponseCache(cache_dir=str(tmp_path / "cache"))

        # 设置缓存
        cache.set("测试问题", "ollama/gemma3", "测试回答")

        # 获取缓存
        cached = cache.get("测试问题", "ollama/gemma3")
        assert cached == "测试回答"

    def test_cache_miss(self, tmp_path):
        """测试缓存未命中"""
        cache = ResponseCache(cache_dir=str(tmp_path / "cache"))

        cached = cache.get("不存在的问题", "ollama/gemma3")
        assert cached is None

    def test_clear(self, tmp_path):
        """测试清空缓存"""
        cache = ResponseCache(cache_dir=str(tmp_path / "cache"))
        cache.set("问题", "model", "回答")

        cache.clear()

        cached = cache.get("问题", "model")
        assert cached is None

    def test_get_stats(self, tmp_path):
        """测试获取统计信息"""
        cache = ResponseCache(cache_dir=str(tmp_path / "cache"))
        cache.set("问题1", "model", "回答1")
        cache.set("问题2", "model", "回答2")

        stats = cache.get_stats()
        assert stats["count"] == 2
        assert stats["total_size"] > 0


class TestEnhancedLLMClient:
    """测试增强的 LLM 客户端"""

    def test_initialization(self):
        """测试初始化"""
        client = EnhancedLLMClient(model="ollama/gemma3")

        assert client.model == "ollama/gemma3"
        assert client.temperature == 0.7
        assert client.max_tokens == 2000
        assert client.max_retries == 3
        assert client.enable_cache is True

    def test_initialization_without_cache(self):
        """测试不启用缓存"""
        client = EnhancedLLMClient(enable_cache=False)
        assert client.enable_cache is False
        assert client.cache is None

    @patch('lobster.core.llm_client.litellm.completion')
    def test_generate(self, mock_completion):
        """测试生成文本"""
        # Mock 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "测试回答"
        mock_completion.return_value = mock_response

        client = EnhancedLLMClient(enable_cache=False)
        result = client.generate("测试问题")

        assert result == "测试回答"
        mock_completion.assert_called_once()

    @patch('lobster.core.llm_client.litellm.completion')
    def test_generate_with_system_prompt(self, mock_completion):
        """测试带系统提示的生成"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "回答"
        mock_completion.return_value = mock_response

        client = EnhancedLLMClient(enable_cache=False)
        result = client.generate("问题", system_prompt="你是一个助手")

        assert result == "回答"

    @patch('lobster.core.llm_client.litellm.completion')
    def test_chat(self, mock_completion):
        """测试多轮对话"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "回复"
        mock_completion.return_value = mock_response

        client = EnhancedLLMClient(enable_cache=False)

        # 第一轮对话
        response1 = client.chat("你好")
        assert response1 == "回复"
        assert len(client.conversation.history) == 2  # user + assistant

        # 第二轮对话
        response2 = client.chat("我刚才说了什么？")
        assert response2 == "回复"
        assert len(client.conversation.history) == 4

    @patch('lobster.core.llm_client.litellm.completion')
    def test_batch_generate(self, mock_completion):
        """测试批量生成"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "回答"
        mock_completion.return_value = mock_response

        client = EnhancedLLMClient(enable_cache=False)
        prompts = ["问题1", "问题2", "问题3"]

        results = client.batch_generate(prompts)

        assert len(results) == 3
        assert all(r == "回答" for r in results)
        assert mock_completion.call_count == 3

    def test_clear_conversation(self):
        """测试清空对话"""
        client = EnhancedLLMClient()
        client.conversation.add_message("user", "测试")

        client.clear_conversation()

        assert len(client.conversation.history) == 0

    def test_get_stats(self):
        """测试获取统计信息"""
        client = EnhancedLLMClient()
        client.conversation.add_message("user", "测试")

        stats = client.get_stats()

        assert "model" in stats
        assert "conversation_length" in stats
        assert stats["conversation_length"] == 1


class TestGetLLMClient:
    """测试获取 LLM 客户端"""

    @patch('lobster.core.config.ConfigManager')
    def test_get_llm_client_default(self, mock_config):
        """测试获取默认客户端"""
        mock_config_instance = MagicMock()
        mock_config_instance.get.return_value = "ollama/gemma3"
        mock_config.return_value = mock_config_instance

        from lobster.core.llm_client import get_llm_client
        client = get_llm_client()

        assert client.model == "ollama/gemma3"

    @patch('lobster.core.config.ConfigManager')
    def test_get_llm_client_custom_model(self, mock_config):
        """测试获取自定义模型客户端"""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        from lobster.core.llm_client import get_llm_client
        client = get_llm_client(model="ollama/llama3")

        assert client.model == "ollama/llama3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
