"""纯文本文档加载器"""
from typing import List
from src.loaders.base import BaseLoader, Document


class TXTLoader(BaseLoader):
    """
    纯文本文档加载器

    处理策略：
    - 整个文件作为 1 个 Document
    - 保留内容完整性，由 split_text() 函数负责后续切分
    - 适用于各种长度的纯文本文件
    """

    def load(self, path: str) -> List[Document]:
        """
        加载纯文本文档

        Args:
            path: 文本文件路径

        Returns:
            文档列表（整个文档作为一个文档）
        """
        path_obj = self.validate_file_path(path, file_type="Text")

        # 读取整个文件内容
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 返回单个 Document，包含完整内容
        return [
            Document(
                content=content,
                metadata={
                    "type": "txt",
                    "file_size": path_obj.stat().st_size,
                    "char_count": len(content),
                },
                source=str(path_obj),
            )
        ]
