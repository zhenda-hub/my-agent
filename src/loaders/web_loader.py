"""网页文档加载器"""
from typing import List
import trafilatura
from src.loaders.base import BaseLoader, Document


class WebLoader(BaseLoader):
    """网页文档加载器"""

    def load(self, url: str) -> List[Document]:
        """
        加载网页内容

        Args:
            url: 网页 URL

        Returns:
            文档列表
        """
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            raise ValueError(f"Failed to fetch URL: {url}")

        content = trafilatura.extract(downloaded)

        if content is None:
            raise ValueError(f"Failed to extract content from: {url}")

        return [
            Document(
                content=content,
                metadata={"type": "web", "url": url},
                source=url,
            )
        ]
