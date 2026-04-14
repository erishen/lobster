"""轻量级 LLM 集成 - 直接使用 LiteLLM"""

from typing import Optional, List, Dict, Any
import litellm
from litellm import completion
from rich.console import Console

console = Console()


class LLMClient:
    """轻量级 LLM 客户端
    
    直接使用 LiteLLM，无需 langchain-llm-toolkit
    """
    
    def __init__(
        self,
        model: str = "ollama/gemma3",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            
        Returns:
            生成的文本
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]LLM 调用失败: {str(e)}[/]")
            return f"错误: {str(e)}"
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ):
        """流式生成文本
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            
        Yields:
            生成的文本片段
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = completion(
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
        messages: List[Dict[str, str]],
    ) -> str:
        """多轮对话
        
        Args:
            messages: 消息列表
            
        Returns:
            助手回复
        """
        try:
            response = completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]LLM 调用失败: {str(e)}[/]")
            return f"错误: {str(e)}"


def get_llm_client(model: Optional[str] = None) -> LLMClient:
    """获取 LLM 客户端
    
    Args:
        model: 模型名称，如果为 None 则使用默认模型
        
    Returns:
        LLM 客户端实例
    """
    from lobster.core.config import ConfigManager
    
    config = ConfigManager()
    default_model = model or config.get('default_model', 'ollama/gemma3')
    
    return LLMClient(model=default_model)
