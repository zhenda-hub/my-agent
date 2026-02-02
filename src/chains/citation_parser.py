"""Citation Parser - Extract and format citations from LLM output"""
import re
from typing import List, Dict, Any
from pathlib import Path
from collections import defaultdict


class CitationParser:
    """解析 LLM 输出中的引用并生成可点击链接"""

    # 支持的引用格式正则模式
    PATTERNS = [
        r'\[参考文档?\s*(\d+)\]',
        r'\[参考\s*(\d+)\]',
        r'\[文档\s*(\d+)\]',
        r'参考文档\s*(\d+)(?:\s|$|[、,，])',
        r'文档\s*(\d+)(?:\s|$|[、,，])',
        r'[\(（]参考文档?\s*(\d+)[\)）]',
        r'[\(（]文档\s*(\d+)[\)）]',
    ]

    def __init__(self, sources: List[Dict[str, Any]]):
        """
        Args:
            sources: 检索到的 chunks 列表
        """
        self.sources = sources
        # 按文档路径分组 chunks
        self.doc_groups = self._group_by_document()

    def _group_by_document(self) -> Dict[str, List[Dict]]:
        """按文档路径分组 chunks"""
        groups = defaultdict(list)
        for source in self.sources:
            doc_path = source.get('source', '')
            groups[doc_path].append(source)
        return dict(groups)

    def _get_doc_name(self, source_path: str) -> str:
        """从路径提取文档名"""
        return Path(source_path).stem

    def parse(self, text: str) -> str:
        """
        解析文本中的引用，返回带可点击链接的 HTML
        """
        # 获取文档路径列表（按检索顺序）
        doc_paths = list(set(s.get('source', '') for s in self.sources))

        matches = []

        for pattern in self.PATTERNS:
            for match in re.finditer(pattern, text):
                try:
                    doc_num = int(match.group(1))
                    if 1 <= doc_num <= len(doc_paths):
                        source_index = doc_num - 1
                        doc_path = doc_paths[source_index]
                        matches.append({
                            'matched_text': match.group(0),
                            'doc_index': source_index,
                            'doc_path': doc_path,
                            'doc_name': self._get_doc_name(doc_path),
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                        })
                except (ValueError, IndexError):
                    continue

        # 按位置倒序替换
        matches.sort(key=lambda m: m['start_pos'], reverse=True)
        processed_text = text

        for match in matches:
            link_html = f'<a href="#" class="citation-link" data-doc-index="{match["doc_index"]}" style="color: #1f77b4; text-decoration: underline; cursor: pointer;">{match["matched_text"]}</a>'
            processed_text = (
                processed_text[:match['start_pos']] +
                link_html +
                processed_text[match['end_pos']:]
            )

        return processed_text

    def get_document_data(self) -> List[Dict]:
        """
        生成文档数据供 JavaScript 使用

        Returns:
            [
                {
                    'doc_index': 0,
                    'doc_name': '文档名',
                    'doc_path': '/path/to/doc',
                    'chunks': [
                        {'content': '...', 'chapter_title': '...', 'page': 1},
                        ...
                    ]
                },
                ...
            ]
        """
        doc_data = []
        doc_paths = list(set(s.get('source', '') for s in self.sources))

        for idx, doc_path in enumerate(doc_paths):
            chunks = self.doc_groups.get(doc_path, [])

            # 提取 chunks 信息
            chunks_info = []
            for chunk in chunks:
                metadata = chunk.get('metadata', {})
                chunks_info.append({
                    'content': chunk.get('content', ''),
                    'chapter_title': metadata.get('chapter_title', ''),
                    'page': metadata.get('page', metadata.get('page_num', 0)),
                    'chunk_index': metadata.get('chunk_index', 0),
                })

            doc_data.append({
                'doc_index': idx,
                'doc_name': self._get_doc_name(doc_path),
                'doc_path': doc_path,
                'chunks': chunks_info,
            })

        return doc_data
