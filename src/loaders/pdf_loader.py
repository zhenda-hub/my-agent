"""PDF 文档加载器"""
from pathlib import Path
from typing import List
import pypdf
from src.loaders.base import BaseLoader, Document


class PDFLoader(BaseLoader):
    """PDF 文档加载器"""

    def load(self, path: str) -> List[Document]:
        """
        加载 PDF 文档

        Args:
            path: PDF 文件路径

        Returns:
            文档列表（每个页面一个文档）
        """
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        documents = []

        with open(path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if text.strip():
                    doc = Document(
                        content=text,
                        metadata={
                            "page": page_num + 1,
                            "total_pages": num_pages,
                            "type": "pdf",
                        },
                        source=str(path_obj),
                    )
                    documents.append(doc)

        return documents
