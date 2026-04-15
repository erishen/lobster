"""增强的 LLM 客户端 - 支持对话管理、批量生成、缓存"""

from typing import Optional, List, Dict, Any
import litellm
from rich.console import Console
from pathlib import Path
import json
from datetime import datetime
import hashlib

console = Console()


class ConversationManager:
    """对话管理器

    管理多轮对话的历史记录
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """添加消息"""
        self.history.append({"role": role, "content": content})

        # 保持历史记录在限制内
        if len(self.history) > self.max_history * 2:
            # 保留系统消息和最近的对话
            system_messages = [m for m in self.history if m["role"] == "system"]
            other_messages = [m for m in self.history if m["role"] != "system"]
            keep_count = self.max_history * 2 - len(system_messages)
            self.history = system_messages + other_messages[-keep_count:]

    def get_messages(self) -> List[Dict[str, str]]:
        """获取所有消息"""
        return self.history.copy()

    def clear(self):
        """清空历史"""
        self.history = []

    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """获取最后 n 条消息"""
        return self.history[-n:] if n > 0 else []

    def export_history(self) -> str:
        """导出历史记录"""
        return json.dumps(self.history, indent=2, ensure_ascii=False)

    def import_history(self, history_json: str):
        """导入历史记录"""
        self.history = json.loads(history_json)


class ResponseCache:
    """响应缓存

    缓存 LLM 响应以减少重复调用
    """

    def __init__(self, cache_dir: str = ".lobster_cache", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl  # 缓存过期时间（秒）

    def _get_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """生成缓存键"""
        cache_data = f"{prompt}:{model}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """获取缓存"""
        cache_key = self._get_cache_key(prompt, model, **kwargs)
        cache_file = self._get_cache_file(cache_key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # 检查是否过期
            cached_time = datetime.fromisoformat(cache_data["timestamp"])
            if (datetime.now() - cached_time).total_seconds() > self.ttl:
                cache_file.unlink()
                return None

            return cache_data["response"]

        except Exception:
            return None

    def set(self, prompt: str, model: str, response: str, **kwargs):
        """设置缓存"""
        cache_key = self._get_cache_key(prompt, model, **kwargs)
        cache_file = self._get_cache_file(cache_key)

        cache_data = {
            "prompt": prompt,
            "model": model,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "kwargs": kwargs,
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def clear(self):
        """清空缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "count": len(cache_files),
            "total_size": total_size,
            "total_size_mb": total_size / (1024 * 1024),
        }


class EnhancedLLMClient:
    """增强的 LLM 客户端

    支持：
    - 对话管理
    - 批量生成
    - 响应缓存
    - 异步生成
    - 重试机制
    """

    def __init__(
        self,
        model: str = "ollama/gemma3",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
        max_retries: int = 3,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries

        # 对话管理
        self.conversation = ConversationManager()

        # 缓存
        self.enable_cache = enable_cache
        self.cache = ResponseCache(ttl=cache_ttl) if enable_cache else None

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_cache: bool = True,
    ) -> str:
        """生成文本

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            use_cache: 是否使用缓存

        Returns:
            生成的文本
        """
        # 检查缓存
        if self.enable_cache and use_cache:
            cached = self.cache.get(prompt, self.model, system_prompt=system_prompt)
            if cached:
                console.print("[dim]使用缓存响应[/]")
                return cached

        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                response = litellm.completion(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

                result = response.choices[0].message.content

                # 保存缓存
                if self.enable_cache and use_cache:
                    self.cache.set(prompt, self.model, result, system_prompt=system_prompt)

                return result

            except Exception as e:
                if attempt == self.max_retries - 1:
                    console.print(f"[red]LLM 调用失败（重试 {self.max_retries} 次后）: {str(e)}[/]")
                    return f"错误: {str(e)}"
                console.print(f"[yellow]LLM 调用失败，重试中... ({attempt + 1}/{self.max_retries})[/]")

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ):
        """流式生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"错误: {str(e)}"

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """多轮对话

        Args:
            message: 用户消息
            system_prompt: 系统提示（仅在首次对话时有效）

        Returns:
            助手回复
        """
        # 如果是首次对话且有系统提示
        if not self.conversation.history and system_prompt:
            self.conversation.add_message("system", system_prompt)

        # 添加用户消息
        self.conversation.add_message("user", message)

        # 调用 LLM
        try:
            response = litellm.completion(
                model=self.model,
                messages=self.conversation.get_messages(),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            assistant_message = response.choices[0].message.content

            # 添加助手消息
            self.conversation.add_message("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            console.print(f"[red]对话失败: {str(e)}[/]")
            return f"错误: {str(e)}"

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
    ) -> List[str]:
        """批量生成

        Args:
            prompts: 提示列表
            system_prompt: 系统提示

        Returns:
            生成的文本列表
        """
        results = []

        for i, prompt in enumerate(prompts, 1):
            console.print(f"[dim]处理 {i}/{len(prompts)}...[/]")
            result = self.generate(prompt, system_prompt)
            results.append(result)

        return results

    def clear_conversation(self):
        """清空对话历史"""
        self.conversation.clear()

    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "model": self.model,
            "conversation_length": len(self.conversation.history),
        }

        if self.cache:
            stats["cache"] = self.cache.get_stats()

        return stats


# 为了向后兼容，保留原来的类名
LLMClient = EnhancedLLMClient


def get_llm_client(model: Optional[str] = None, **kwargs) -> EnhancedLLMClient:
    """获取 LLM 客户端"""
    from lobster.core.config import ConfigManager

    config = ConfigManager()
    default_model = model or config.get("default_model", "ollama/gemma3")

    return EnhancedLLMClient(model=default_model, **kwargs)
