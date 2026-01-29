"""章节检测器 - 从文档中提取章节结构"""
from dataclasses import dataclass
from typing import List
import re
from pathlib import Path


@dataclass
class ChapterInfo:
    """章节信息"""
    chapter_id: str
    title: str
    level: int  # 1=主章节, 2=子节, 3=小节
    page_num: int = 0
    line_start: int = 0
    line_end: int = 0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "chapter_id": self.chapter_id,
            "title": self.title,
            "level": self.level,
            "page_num": self.page_num,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


class ChapterDetector:
    """章节检测器 - 支持多种文档格式"""

    # 常见章节标题的正则模式
    PATTERNS = [
        # 英文章节格式
        (r"^Chapter\s+\d+[:\.\s]*.*", 1),
        (r"^\d+\.\s+[\w\s]+", 2),
        # 中文章节格式
        (r"^第[一二三四五六七八九十百千\d]+章[：:\s]*.*", 1),
        (r"^第[一二三四五六七八九十百千\d]+节[：:\s]*.*", 2),
        (r"^\d+、[\w\u4e00-\u9fff]+", 2),
        # Markdown 标题
        (r"^#{1,3}\s+.+", 1),
    ]

    def detect_txt_chapters(self, content: str) -> List[ChapterInfo]:
        """
        检测 TXT 文件中的章节

        Args:
            content: TXT 文本内容

        Returns:
            章节信息列表
        """
        chapters = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 检查是否匹配章节标题模式
            for pattern, level in self.PATTERNS:
                if re.match(pattern, line, re.MULTILINE):
                    chapter = ChapterInfo(
                        chapter_id=f"ch_{len(chapters) + 1}",
                        title=line,
                        level=level,
                        line_start=line_num + 1,
                    )
                    chapters.append(chapter)
                    break

        # 设置章节结束行号
        for i in range(len(chapters) - 1):
            chapters[i].line_end = chapters[i + 1].line_start - 1

        if chapters:
            chapters[-1].line_end = len(lines)

        return chapters

    def detect_epub_chapters(self, epub_path: str) -> List[ChapterInfo]:
        """
        从 EPUB 文件中提取章节目录

        Args:
            epub_path: EPUB 文件路径

        Returns:
            章节信息列表
        """
        try:
            import ebooklib
            from ebooklib import epub
        except ImportError:
            raise ImportError("请安装 ebooklib: pip install ebooklib")

        chapters = []

        try:
            book = epub.read_epub(epub_path)
            toc = book.get_table_of_contents()

            def process_toc_item(item, level=0, chapter_num=0):
                if isinstance(item, (list, tuple)):
                    for sub_item in item:
                        chapter_num = process_toc_item(sub_item, level, chapter_num)
                elif isinstance(item, ebooklib.epub.Link):
                    chapters.append(ChapterInfo(
                        chapter_id=f"ch_{chapter_num + 1}",
                        title=item.title or f"Chapter {chapter_num + 1}",
                        level=level,
                    ))
                    return chapter_num + 1
                elif isinstance(item, ebooklib.epub.Section):
                    for sub_item in item:
                        chapter_num = process_toc_item(sub_item, level + 1, chapter_num)
                return chapter_num

            process_toc_item(toc)

        except Exception as e:
            # 如果无法解析目录，返回空列表
            pass

        return chapters

    def detect_pdf_chapters(self, pdf_path: str) -> List[ChapterInfo]:
        """
        检测 PDF 文件中的章节（基于字体大小）

        Args:
            pdf_path: PDF 文件路径

        Returns:
            章节信息列表
        """
        # PDF 章节检测需要更复杂的逻辑
        # 这里提供基本实现，可以后续扩展
        chapters = []

        try:
            import pypdf

            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                num_pages = len(reader.pages)

                # 简单策略：检测每页开头的大号字体文本
                for page_num in range(min(num_pages, 10)):  # 只检查前10页
                    page = reader.pages[page_num]
                    text = page.extract_text()

                    if text:
                        lines = text.split('\n')
                        for line in lines[:5]:  # 只检查前5行
                            line = line.strip()
                            if len(line) < 5:  # 跳过太短的行
                                continue

                            # 检查是否匹配章节模式
                            for pattern, level in self.PATTERNS:
                                if re.match(pattern, line):
                                    chapters.append(ChapterInfo(
                                        chapter_id=f"ch_{len(chapters) + 1}",
                                        title=line,
                                        level=level,
                                        page_num=page_num + 1,
                                    ))
                                    break

        except Exception as e:
            pass

        return chapters
