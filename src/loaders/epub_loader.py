"""EPUB 电子书加载器"""
from pathlib import Path
from typing import List
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from src.loaders.base import BaseLoader, Document


class EPUBLoader(BaseLoader):
    """EPUB 电子书加载器"""

    def load(self, path: str) -> List[Document]:
        """
        加载 EPUB 电子书

        Args:
            path: EPUB 文件路径

        Returns:
            文档列表（每个章节一个文档）
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"EPUB file not found: {path}")

        documents = []

        try:
            # 读取 EPUB 文件
            book = epub.read_epub(path)

            # 获取目录结构
            toc = book.get_table_of_contents()
            chapters_info = self._extract_chapters_info(toc)

            # 获取所有 HTML 内容
            items = list(book.get_items())
            epub_items = [item for item in items if isinstance(item, ebooklib.epub.EpubHtml)]

            # 按章节提取内容
            for idx, item in enumerate(epub_items):
                # 获取章节名称
                chapter_name = item.get_name()
                chapter_title = self._get_chapter_title(chapter_name, chapters_info, book)

                # 提取文本内容
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                text = soup.get_text(separator='\n', strip=True)

                if text.strip():
                    # 获取文件名作为书名
                    book_title = path_obj.stem

                    doc = Document(
                        content=text,
                        metadata={
                            "chapter_id": f"ch_{idx + 1}",
                            "chapter_title": chapter_title,
                            "chapter_name": chapter_name,
                            "type": "epub",
                            "book_title": book_title,
                        },
                        source=str(path_obj),
                    )
                    documents.append(doc)

        except Exception as e:
            raise RuntimeError(f"Failed to load EPUB file: {e}")

        return documents

    def _extract_chapters_info(self, toc) -> List[dict]:
        """从目录结构中提取章节信息"""
        chapters = []

        def process_toc_item(item, level=0):
            if isinstance(item, (list, tuple)):
                for sub_item in item:
                    process_toc_item(sub_item, level)
            elif isinstance(item, ebooklib.epub.Link):
                chapters.append({
                    "title": item.title,
                    "href": item.href,
                    "level": level,
                })
            elif isinstance(item, ebooklib.epub.Section):
                for sub_item in item:
                    process_toc_item(sub_item, level + 1)

        process_toc_item(toc)
        return chapters

    def _get_chapter_title(self, chapter_name: str, chapters_info: List[dict], book) -> str:
        """根据章节名称获取章节标题"""
        # 从目录信息中查找
        for chapter in chapters_info:
            if chapter["href"].startswith(chapter_name) or chapter_name in chapter["href"]:
                return chapter["title"]

        # 如果找不到，尝试从文件名提取
        name = chapter_name.replace('_', ' ').replace('-', ' ').title()
        return name
