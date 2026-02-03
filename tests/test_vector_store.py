"""VectorStore 单元测试"""
import pytest
from src.vector_store import VectorStore
from src.loaders.base import Document


def test_get_all_sources_empty():
    """测试空数据库的 get_all_sources"""
    vs = VectorStore(collection_name="test_empty")
    vs.clear()
    sources = vs.get_all_sources()
    assert sources == []


def test_get_all_sources():
    """测试获取所有来源"""
    vs = VectorStore(collection_name="test_sources")
    vs.clear()

    # 添加测试文档
    docs = [
        Document(content="test1", metadata={}, source="/path/file1.pdf"),
        Document(content="test2", metadata={}, source="/path/file2.pdf"),
    ]
    vs.add_documents(docs)

    sources = vs.get_all_sources()
    assert set(sources) == {"/path/file1.pdf", "/path/file2.pdf"}


def test_get_all_sources_dedup():
    """测试去重功能 - 同一来源有多个文档块"""
    vs = VectorStore(collection_name="test_dedup")
    vs.clear()

    # 同一来源添加多个文档块
    docs = [
        Document(content="chunk1", metadata={}, source="/path/same_file.pdf"),
        Document(content="chunk2", metadata={}, source="/path/same_file.pdf"),
        Document(content="chunk3", metadata={}, source="/path/same_file.pdf"),
    ]
    vs.add_documents(docs)

    sources = vs.get_all_sources()
    assert sources == ["/path/same_file.pdf"]
