"""文档加载器模块"""
from src.loaders.base import BaseLoader, Document
from src.loaders.pdf_loader import PDFLoader
from src.loaders.docx_loader import DocxLoader
from src.loaders.markdown_loader import MarkdownLoader
from src.loaders.web_loader import WebLoader


# 文件扩展名到加载器的映射
LOADER_MAPPING = {
    ".pdf": PDFLoader,
    ".docx": DocxLoader,
    ".doc": DocxLoader,
    ".md": MarkdownLoader,
    ".markdown": MarkdownLoader,
}


def get_loader(file_path: str) -> BaseLoader:
    """
    根据文件扩展名获取对应的加载器

    Args:
        file_path: 文件路径

    Returns:
        对应的文档加载器
    """
    from pathlib import Path

    ext = Path(file_path).suffix.lower()

    if ext in LOADER_MAPPING:
        return LOADER_MAPPING[ext]()

    raise ValueError(f"Unsupported file type: {ext}")


__all__ = [
    "BaseLoader",
    "Document",
    "PDFLoader",
    "DocxLoader",
    "MarkdownLoader",
    "WebLoader",
    "get_loader",
]
