"""Markdown 文档加载器"""
from pathlib import Path
from typing import List
from src.loaders.base import BaseLoader, Document


class MarkdownLoader(BaseLoader):
    """Markdown 文档加载器"""

    def load(self, path: str) -> List[Document]:
        """
        加载 Markdown 文档

        Args:
            path: Markdown 文件路径

        Returns:
            文档列表（整个文档作为一个文档）
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Markdown file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return [
            Document(
                content=content,
                metadata={"type": "markdown"},
                source=str(path_obj),
            )
        ]
