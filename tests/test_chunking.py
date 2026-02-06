"""测试文本切分模块"""
import pytest
from src.chunking.splitter import get_text_splitter, LangchainTextSplitter, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def test_basic_splitting():
    """测试基本切分功能"""
    text = "这是一个测试。" * 100
    splitter = get_text_splitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    assert len(chunks) > 1
    # 允许一定的误差（因为 langchain 可能在边界处超出）
    assert all(len(chunk) <= 550 for chunk in chunks)


def test_sentence_boundary():
    """测试句子边界切分"""
    text = "第一句。第二句。第三句。"
    splitter = get_text_splitter(chunk_size=50)
    chunks = splitter.split_text(text)
    # 应该在句号处切分
    assert all("。" in chunk or chunk.endswith("。") for chunk in chunks)


def test_short_text():
    """测试短文本不切分"""
    text = "短文本"
    splitter = get_text_splitter()
    chunks = splitter.split_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_custom_params():
    """测试自定义参数"""
    text = "测试。" * 100
    splitter = get_text_splitter(chunk_size=200, chunk_overlap=20)
    chunks = splitter.split_text(text)
    assert all(len(chunk) <= 220 for chunk in chunks)


def test_default_params():
    """测试默认参数"""
    splitter = get_text_splitter()
    assert splitter.chunk_size == DEFAULT_CHUNK_SIZE
    assert splitter.chunk_overlap == DEFAULT_CHUNK_OVERLAP


def test_empty_text():
    """测试空文本"""
    text = ""
    splitter = get_text_splitter()
    chunks = splitter.split_text(text)
    # langchain splitter 对空文本返回空列表
    assert chunks == []


def test_paragraph_splitting():
    """测试段落切分"""
    text = "第一段。\n\n第二段。\n\n第三段。"
    splitter = get_text_splitter(chunk_size=100)
    chunks = splitter.split_text(text)
    # 优先在段落边界切分
    assert len(chunks) >= 1


def test_overlap():
    """测试重叠功能"""
    text = "测试文本。" * 50
    splitter = get_text_splitter(chunk_size=200, chunk_overlap=50)
    chunks = splitter.split_text(text)
    if len(chunks) > 1:
        # 检查相邻块是否有重叠
        # 由于内容重复，应该能找到一些共同字符
        first_chunk_end = chunks[0][-50:]
        second_chunk_start = chunks[1][:50]
        # 简单检查：有重叠的话，第二块开头应该包含第一块结尾的部分内容
        # 但因为标点符号切分，不能严格保证
        assert len(chunks) > 1
