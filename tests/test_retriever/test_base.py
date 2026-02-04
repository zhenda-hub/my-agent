"""测试 Retriever 检索器"""
import pytest
from unittest.mock import Mock, patch
from src.retriever.base import Retriever


class TestRetriever:
    """测试 Retriever 类"""

    def test_retrieve_with_results(self):
        """测试基本检索功能"""
        # Mock vector store
        mock_store = Mock()
        mock_store.search.return_value = [
            {"content": "test content 1", "metadata": {"source": "doc1.pdf"}},
            {"content": "test content 2", "metadata": {"source": "doc2.pdf"}},
        ]

        retriever = Retriever(top_k=2, vector_store=mock_store)
        results = retriever.retrieve("test query")

        assert len(results) == 2
        assert results[0]["content"] == "test content 1"
        mock_store.search.assert_called_once()

    def test_retrieve_empty_results(self):
        """测试空结果检索"""
        mock_store = Mock()
        mock_store.search.return_value = []

        retriever = Retriever(vector_store=mock_store)
        results = retriever.retrieve("no results query")

        assert results == []

    def test_get_context(self):
        """测试上下文构建"""
        mock_store = Mock()
        mock_store.search.return_value = [
            {"content": "content 1", "metadata": {"source": "doc1.pdf"}},
            {"content": "content 2", "metadata": {"source": "doc2.pdf"}},
        ]

        retriever = Retriever(vector_store=mock_store)
        context = retriever.get_context("test query")

        assert "[参考 1]" in context
        assert "doc1.pdf" in context
        assert "content 1" in context

    def test_get_context_empty_results(self):
        """测试空结果时上下文"""
        mock_store = Mock()
        mock_store.search.return_value = []

        retriever = Retriever(vector_store=mock_store)
        context = retriever.get_context("test query")

        assert context == "未找到相关文档。"

    def test_get_sources(self):
        """测试来源提取"""
        mock_store = Mock()
        mock_store.search.return_value = [
            {
                "content": "test content",
                "metadata": {"source": "doc1.pdf", "page": 1}
            },
        ]

        retriever = Retriever(vector_store=mock_store)
        sources = retriever.get_sources("test query")

        assert len(sources) == 1
        assert sources[0]["content"] == "test content"
        assert sources[0]["source"] == "doc1.pdf"
        assert sources[0]["metadata"]["page"] == 1

    def test_custom_vector_store(self):
        """测试自定义向量存储"""
        mock_store = Mock()
        mock_store.search.return_value = []

        retriever = Retriever(vector_store=mock_store)
        _ = retriever.retrieve("test")

        # 验证使用了传入的 vector_store
        assert retriever._vector_store is mock_store

    def test_top_k_parameter(self):
        """测试 top_k 参数传递"""
        mock_store = Mock()
        mock_store.search.return_value = []

        retriever = Retriever(top_k=5, vector_store=mock_store)
        retriever.retrieve("test")

        # 验证 top_k 被传递给 search
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["top_k"] == 5

    def test_filter_metadata(self):
        """测试元数据过滤"""
        mock_store = Mock()
        mock_store.search.return_value = []

        filter_meta = {"type": "pdf"}
        retriever = Retriever(filter_metadata=filter_meta, vector_store=mock_store)
        retriever.retrieve("test")

        # 验证 filter 被传递给 search
        call_kwargs = mock_store.search.call_args[1]
        assert call_kwargs["filter"] == filter_meta
