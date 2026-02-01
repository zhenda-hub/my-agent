"""RAG 检索器模块"""
from typing import List, Dict, Any, Optional
from src.vector_store import get_vector_store


class Retriever:
    """RAG 检索器"""

    def __init__(
        self,
        top_k: int = None,
        filter_metadata: Dict[str, Any] = None,
        vector_store=None,
    ):
        """
        初始化检索器

        Args:
            top_k: 返回结果数量
            filter_metadata: 元数据过滤条件
            vector_store: 可选的向量存储实例（用于使用特定的 vector_store）
        """
        self.top_k = top_k
        self.filter_metadata = filter_metadata
        self._vector_store = vector_store

    @property
    def vector_store(self):
        """获取向量存储实例"""
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        检索相关文档

        Args:
            query: 查询文本

        Returns:
            检索结果列表
        """
        return self.vector_store.search(
            query=query,
            top_k=self.top_k,
            filter=self.filter_metadata,
        )

    def get_context(self, query: str) -> str:
        """
        获取检索到的上下文文本

        Args:
            query: 查询文本

        Returns:
            合并后的上下文文本
        """
        results = self.retrieve(query)

        if not results:
            return "未找到相关文档。"

        context_parts = []
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "未知来源")
            content = result["content"]
            context_parts.append(f"[参考 {i}] 来源: {source}\n{content}")

        return "\n\n".join(context_parts)

    def get_sources(self, query: str) -> List[Dict[str, Any]]:
        """
        获取带来源信息的检索结果

        Args:
            query: 查询文本

        Returns:
            来源信息列表
        """
        results = self.retrieve(query)

        sources = []
        for result in results:
            sources.append({
                "content": result["content"],
                "source": result["metadata"].get("source", "未知来源"),
                "metadata": result["metadata"],
            })

        return sources
