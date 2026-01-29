"""RAG 问答链模块"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from src.config import config
from src.retriever.base import Retriever
from src.chains.llm_manager import LLMManager


@dataclass
class Citation:
    """精确引用信息"""
    book_title: str
    chapter_title: str
    page_num: int
    excerpt: str
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "book_title": self.book_title,
            "chapter_title": self.chapter_title,
            "page_num": self.page_num,
            "excerpt": self.excerpt,
            "confidence": self.confidence,
        }

    def format(self, language: str = "zh") -> str:
        """
        格式化引用

        Args:
            language: 语言，zh=中文, en=英文

        Returns:
            格式化的引用文本
        """
        if language == "zh":
            return f'根据《{self.book_title}》{self.chapter_title}（第{self.page_num}页）："{self.excerpt}"'
        else:
            return f'According to "{self.book_title}", {self.chapter_title} (page {self.page_num}): "{self.excerpt}"'


@dataclass
class QAResult:
    """问答结果"""
    answer: str
    sources: List[Dict[str, Any]]
    citations: List[Citation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "answer": self.answer,
            "sources": self.sources,
            "citations": [c.to_dict() for c in self.citations],
        }


class QAChain:
    """RAG 问答链"""

    # 提示词模板
    SYSTEM_PROMPT = """你是一个专业的知识库助手。请根据以下参考文档回答用户的问题。

要求：
1. 只根据提供的参考文档回答问题，不要使用外部知识
2. 如果参考文档中没有相关信息，请明确说明"根据提供的文档，我无法回答这个问题"
3. 回答要准确、简洁、有条理
4. 必要时引用参考文档中的具体内容

参考文档：
{context}

用户问题：
{question}

请回答："""

    def __init__(
        self,
        retriever: Retriever = None,
        llm_manager: LLMManager = None,
    ):
        """
        初始化问答链

        Args:
            retriever: 检索器实例
            llm_manager: LLM 管理器实例
        """
        self.retriever = retriever or Retriever()
        self.llm_manager = llm_manager

    @property
    def llm(self) -> LLMManager:
        """获取 LLM 实例"""
        if self.llm_manager is None:
            # 使用 DeepSeek 作为默认模型
            try:
                self.llm_manager = LLMManager(default_model="deepseek")
            except ValueError:
                # 如果没有 API key，使用 DeepSeek 直连方式
                from langchain_community.llms import HuggingFacePipeline
                import os
                self.llm_manager = None
        return self.llm_manager

    def run(self, query: str) -> QAResult:
        """
        运行问答链

        Args:
            query: 用户问题

        Returns:
            问答结果（包含答案、来源和引用）
        """
        # 检索相关文档
        sources = self.retriever.get_sources(query)

        # 如果没有检索到相关文档
        if not sources:
            return QAResult(
                answer="抱歉，我在知识库中没有找到与您的问题相关的信息。",
                sources=[],
                citations=[],
            )

        # 构建上下文
        context = self._build_context(sources)

        # 构建提示词
        prompt = self.SYSTEM_PROMPT.format(
            context=context,
            question=query,
        )

        # 调用 LLM
        if self.llm_manager:
            answer = self.llm_manager.generate(prompt)
        else:
            # 如果没有 LLM 管理器，返回简单回答
            answer = f"根据知识库找到 {len(sources)} 个相关文档。请配置 LLM API 获取完整回答。"

        # 生成引用
        citations = self._generate_citations(sources)

        # 返回结果（带来源和引用）
        return QAResult(
            answer=answer,
            sources=sources,
            citations=citations,
        )

    def _generate_citations(self, sources: List[Dict[str, Any]]) -> List[Citation]:
        """
        从检索结果生成引用信息

        Args:
            sources: 检索到的来源列表

        Returns:
            引用信息列表
        """
        citations = []

        for source in sources:
            metadata = source.get("metadata", {})
            content = source.get("content", "")

            # 提取引用信息
            book_title = metadata.get("book_title", Path(source.get("source", "")).stem)
            chapter_title = metadata.get("chapter_title", "未知章节")
            page_num = metadata.get("page", metadata.get("page_num", 0))

            # 取内容前100个字符作为摘录
            excerpt = content[:100] + "..." if len(content) > 100 else content

            citation = Citation(
                book_title=book_title,
                chapter_title=chapter_title,
                page_num=page_num,
                excerpt=excerpt,
            )
            citations.append(citation)

        return citations

    def _build_context(self, sources: List[Dict[str, Any]]) -> str:
        """
        构建上下文文本

        Args:
            sources: 检索到的来源列表

        Returns:
            格式化的上下文文本
        """
        context_parts = []

        for i, source in enumerate(sources, 1):
            source_file = source.get("source", "未知来源")
            content = source.get("content", "")
            context_parts.append(
                f"[参考文档 {i}]\n"
                f"来源：{source_file}\n"
                f"内容：{content}"
            )

        return "\n\n".join(context_parts)

    async def arun(self, query: str) -> QAResult:
        """
        异步运行问答链

        Args:
            query: 用户问题

        Returns:
            问答结果（包含答案和来源）
        """
        # 同步版本的异步包装
        # 对于真正的异步实现，需要使用异步 LLM
        return self.run(query)
