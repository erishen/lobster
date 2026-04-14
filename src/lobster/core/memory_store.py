"""简单的向量存储 - 用于记忆功能"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib


class SimpleVectorStore:
    """简单的向量存储
    
    使用文件存储，无需复杂的向量数据库
    """
    
    def __init__(self, storage_path: str = ".lobster_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self._load_index()
    
    def _load_index(self):
        """加载索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = []
    
    def _save_index(self):
        """保存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """添加内容
        
        Args:
            content: 内容
            metadata: 元数据
            
        Returns:
            内容 ID
        """
        content_id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        entry = {
            "id": content_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }
        
        self.index.append(entry)
        self._save_index()
        
        return content_id
    
    def search(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """搜索内容（简单的关键词匹配）
        
        Args:
            query: 查询字符串
            k: 返回数量
            
        Returns:
            匹配的内容列表
        """
        query_lower = query.lower()
        results = []
        
        for entry in self.index:
            content_lower = entry["content"].lower()
            
            # 简单的关键词匹配
            if query_lower in content_lower:
                results.append(entry)
        
        # 按时间倒序
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return results[:k]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有内容"""
        return self.index
    
    def delete(self, content_id: str) -> bool:
        """删除内容
        
        Args:
            content_id: 内容 ID
            
        Returns:
            是否成功
        """
        for i, entry in enumerate(self.index):
            if entry["id"] == content_id:
                self.index.pop(i)
                self._save_index()
                return True
        return False
    
    def clear(self):
        """清空所有内容"""
        self.index = []
        self._save_index()
    
    def count(self) -> int:
        """获取内容数量"""
        return len(self.index)


class MemoryManager:
    """记忆管理器
    
    使用简单的向量存储管理记忆
    """
    
    def __init__(self, storage_path: str = ".lobster_memory"):
        self.store = SimpleVectorStore(storage_path)
    
    def add_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
    ) -> str:
        """添加记忆
        
        Args:
            content: 记忆内容
            tags: 标签列表
            category: 分类
            
        Returns:
            记忆 ID
        """
        metadata = {
            "tags": tags or [],
            "category": category,
        }
        
        return self.store.add(content, metadata)
    
    def search_memory(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """搜索记忆
        
        Args:
            query: 查询字符串
            k: 返回数量
            
        Returns:
            匹配的记忆列表
        """
        return self.store.search(query, k)
    
    def list_memories(self) -> List[Dict[str, Any]]:
        """列出所有记忆"""
        return self.store.get_all()
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        return self.store.delete(memory_id)
    
    def clear_memories(self):
        """清空所有记忆"""
        self.store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        memories = self.store.get_all()
        
        stats = {
            "total": len(memories),
            "categories": {},
            "tags": {},
        }
        
        for memory in memories:
            # 统计分类
            category = memory.get("metadata", {}).get("category", "general")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            # 统计标签
            tags = memory.get("metadata", {}).get("tags", [])
            for tag in tags:
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1
        
        return stats
