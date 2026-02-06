"""文本切分模块 - 统一的文档切分接口"""
from typing import List, Protocol
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 默认切分参数
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


class TextSplitter(Protocol):
    """文本切分器协议"""

    def split_text(self, text: str) -> List[str]:
        """切分文本"""
        ...


class LangchainTextSplitter:
    """基于 langchain 的文本切分器"""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        separators: List[str] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", ".", " ", ""]

        self._splitter = RecursiveCharacterTextSplitter(
            separators=self.separators,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def split_text(self, text: str) -> List[str]:
        return self._splitter.split_text(text)


def get_text_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> TextSplitter:
    """获取文本切分器实例"""
    return LangchainTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
