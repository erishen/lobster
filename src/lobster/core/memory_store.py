"""优化的向量存储 - 支持相似度搜索和模糊匹配"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import re
from collections import Counter
import math


class OptimizedVectorStore:
    """优化的向量存储

    支持：
    - 关键词匹配
    - 相似度计算（TF-IDF）
    - 模糊搜索
    """

    def __init__(self, storage_path: str = ".lobster_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self._load_index()

    def _load_index(self):
        """加载索引"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = []

    def _save_index(self):
        """保存索引"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def _tokenize(self, text: str) -> List[str]:
        """分词

        Args:
            text: 文本

        Returns:
            词列表
        """
        # 简单的分词：按空格和标点符号分割
        text = text.lower()
        tokens = re.findall(r"\b\w+\b", text)
        return tokens

    def _calculate_tfidf(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        """计算 TF-IDF 相似度

        Args:
            query_tokens: 查询词列表
            doc_tokens: 文档词列表

        Returns:
            相似度分数
        """
        if not query_tokens or not doc_tokens:
            return 0.0

        # 计算词频
        query_tf = Counter(query_tokens)
        doc_tf = Counter(doc_tokens)

        # 计算交集
        common_tokens = set(query_tf.keys()) & set(doc_tf.keys())

        if not common_tokens:
            return 0.0

        # 简化的 TF-IDF 计算
        score = 0.0
        for token in common_tokens:
            # TF: 词在文档中的频率
            tf = doc_tf[token] / len(doc_tokens)

            # IDF: 简化计算，使用词在查询中的重要性
            idf = math.log(len(query_tokens) / query_tf[token] + 1)

            score += tf * idf

        return score

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离

        Args:
            s1: 字符串1
            s2: 字符串2

        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _fuzzy_match(self, s1: str, s2: str, threshold: float = 0.7) -> bool:
        """模糊匹配

        Args:
            s1: 字符串1
            s2: 字符串2
            threshold: 阈值

        Returns:
            是否匹配
        """
        if not s1 or not s2:
            return False

        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return True

        distance = self._levenshtein_distance(s1.lower(), s2.lower())
        similarity = 1 - (distance / max_len)

        return similarity >= threshold

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

        # 预计算词频
        tokens = self._tokenize(content)
        token_freq = dict(Counter(tokens))

        entry = {
            "id": content_id,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens,
            "token_freq": token_freq,
        }

        self.index.append(entry)
        self._save_index()

        return content_id

    def search(
        self,
        query: str,
        k: int = 5,
        method: str = "keyword",
    ) -> List[Dict[str, Any]]:
        """搜索内容

        Args:
            query: 查询字符串
            k: 返回数量
            method: 搜索方法 (keyword/similarity/fuzzy)

        Returns:
            匹配的内容列表
        """
        if method == "keyword":
            return self._search_keyword(query, k)
        elif method == "similarity":
            return self._search_similarity(query, k)
        elif method == "fuzzy":
            return self._search_fuzzy(query, k)
        else:
            return self._search_keyword(query, k)

    def _search_keyword(self, query: str, k: int) -> List[Dict[str, Any]]:
        """关键词搜索"""
        query_lower = query.lower()
        results = []

        for entry in self.index:
            content_lower = entry["content"].lower()
            if query_lower in content_lower:
                results.append(entry)

        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results[:k]

    def _search_similarity(self, query: str, k: int) -> List[Dict[str, Any]]:
        """相似度搜索"""
        query_tokens = self._tokenize(query)
        scored_results = []

        for entry in self.index:
            doc_tokens = entry.get("tokens", self._tokenize(entry["content"]))
            score = self._calculate_tfidf(query_tokens, doc_tokens)

            if score > 0:
                scored_results.append((score, entry))

        # 按分数排序
        scored_results.sort(key=lambda x: x[0], reverse=True)

        return [entry for score, entry in scored_results[:k]]

    def _search_fuzzy(self, query: str, k: int) -> List[Dict[str, Any]]:
        """模糊搜索"""
        query_tokens = self._tokenize(query)
        results = []

        for entry in self.index:
            content = entry["content"]
            content_tokens = entry.get("tokens", self._tokenize(content))

            # 检查是否有模糊匹配的词
            matched = False
            for q_token in query_tokens:
                for c_token in content_tokens:
                    if self._fuzzy_match(q_token, c_token, threshold=0.7):
                        matched = True
                        break
                if matched:
                    break

            if matched:
                results.append(entry)

        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results[:k]

    def search_hybrid(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """混合搜索（关键词 + 相似度）

        Args:
            query: 查询字符串
            k: 返回数量

        Returns:
            匹配的内容列表
        """
        # 获取关键词匹配结果
        keyword_results = self._search_keyword(query, k * 2)

        # 获取相似度匹配结果
        similarity_results = self._search_similarity(query, k * 2)

        # 合并结果，去重
        seen_ids = set()
        merged_results = []

        # 优先添加关键词匹配
        for entry in keyword_results:
            if entry["id"] not in seen_ids:
                merged_results.append(entry)
                seen_ids.add(entry["id"])

        # 添加相似度匹配
        for entry in similarity_results:
            if entry["id"] not in seen_ids:
                merged_results.append(entry)
                seen_ids.add(entry["id"])

        return merged_results[:k]

    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有内容"""
        return self.index

    def delete(self, content_id: str) -> bool:
        """删除内容"""
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


class EnhancedMemoryManager:
    """增强的记忆管理器

    支持多种搜索方式
    """

    def __init__(self, storage_path: str = ".lobster_memory"):
        self.store = OptimizedVectorStore(storage_path)

    def add_memory(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
    ) -> str:
        """添加记忆"""
        metadata = {
            "tags": tags or [],
            "category": category,
        }

        return self.store.add(content, metadata)

    def search_memory(
        self,
        query: str,
        k: int = 5,
        method: str = "hybrid",
    ) -> List[Dict[str, Any]]:
        """搜索记忆

        Args:
            query: 查询字符串
            k: 返回数量
            method: 搜索方法 (keyword/similarity/fuzzy/hybrid)

        Returns:
            匹配的记忆列表
        """
        if method == "hybrid":
            return self.store.search_hybrid(query, k)
        else:
            return self.store.search(query, k, method)

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
            category = memory.get("metadata", {}).get("category", "general")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

            tags = memory.get("metadata", {}).get("tags", [])
            for tag in tags:
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1

        return stats
