"""基础文档加载器"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Document:
    """文档数据类"""
    content: str
    metadata: Dict[str, Any]
    source: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "source": self.source,
        }


class BaseLoader(ABC):
    """文档加载器基类"""

    @abstractmethod
    def load(self, path: str) -> List[Document]:
        """
        加载文档

        Args:
            path: 文档路径

        Returns:
            文档列表
        """
        pass
