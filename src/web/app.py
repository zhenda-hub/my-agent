"""Gradio Web 界面 - Book RAG"""
import gradio as gr
from pathlib import Path
from typing import List, Tuple, Optional


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """将文本切分成小块"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # 尝试在句号、换行符等位置切分
        if end < len(text):
            period_pos = text.rfind("。", start, end)
            exclamation_pos = text.rfind("！", start, end)
            question_pos = text.rfind("？", start, end)
            newline_pos = text.rfind("\n", start, end)

            best_pos = max(period_pos, exclamation_pos, question_pos, newline_pos)
            if best_pos > start + chunk_size // 2:
                end = best_pos + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end < len(text) else end

    return chunks


# 全局状态
class SessionState:
    """会话状态管理"""
    def __init__(self):
        self.api_key: Optional[str] = None
        self.model: str = "deepseek"
        self.llm_manager = None
        self._vector_store = None
        self._embeddings = None
        self.documents_loaded: bool = False

    @property
    def embeddings(self):
        """延迟加载 embeddings"""
        if self._embeddings is None:
            from src.embeddings import get_embeddings
            self._embeddings = get_embeddings()
        return self._embeddings

    @property
    def vector_store(self):
        """延迟加载向量存储"""
        if self._vector_store is None:
            from src.vector_store import get_vector_store
            self._vector_store = get_vector_store()
        return self._vector_store


# 模型选项
MODEL_OPTIONS = [
    "deepseek",
    "deepseek-reasoner",
    "gpt-4",
    "gpt-3.5",
    "claude-opus",
    "claude-sonnet",
    "gemini",
    "llama",
]


def process_upload(files: List, state: SessionState) -> str:
    """处理文件上传"""
    if not files:
        return "❌ 请选择文件"

    count = 0
    results = []
    total_chunks = 0

    from src.loaders import get_loader
    from src.loaders.base import Document

    for file in files:
        file_path = file.name
        path = Path(file_path)

        try:
            # 获取加载器
            loader = get_loader(str(path))

            # 加载文档
            documents = loader.load(str(path))

            # 切分文档
            chunked_docs = []
            for doc in documents:
                chunks = split_text(doc.content)
                for i, chunk in enumerate(chunks):
                    chunked_doc = Document(
                        content=chunk,
                        metadata={
                            **doc.metadata,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                        },
                        source=doc.source,
                    )
                    chunked_docs.append(chunked_doc)

            # 清除旧数据
            state.vector_store.delete_by_source(str(path))

            # 添加到向量存储
            state.vector_store.add_documents(chunked_docs)

            count += 1
            total_chunks += len(chunked_docs)
            results.append(f"✅ {path.name}: {len(chunked_docs)} 个块")

        except Exception as e:
            results.append(f"❌ {path.name}: {str(e)}")

    state.documents_loaded = count > 0

    summary = f"📊 已上传 {count} 个文件，共 {total_chunks} 个文档块\n\n" + "\n".join(results)
    return summary


def chat_response(
    message: str,
    history: List[Tuple[str, str]],
    api_key: str,
    model: str,
    state: SessionState,
) -> List[Tuple[str, str]]:
    """处理问答"""
    if not message.strip():
        return history

    # 检查 API Key
    if not api_key:
        history.append((message, "⚠️ 请先配置 OpenRouter API Key"))
        return history

    # 更新 LLM 管理器
    if api_key != state.api_key or model != state.model:
        from src.chains.llm_manager import LLMManager
        state.api_key = api_key
        state.model = model
        state.llm_manager = LLMManager(api_key=api_key, default_model=model)
    elif state.llm_manager is None:
        from src.chains.llm_manager import LLMManager
        state.llm_manager = LLMManager(api_key=api_key, default_model=model)

    # 检查文档
    if not state.documents_loaded:
        history.append((message, "⚠️ 请先上传文档"))
        return history

    try:
        from src.chains.qa_chain import QAChain
        from src.retriever.base import Retriever

        # 创建 QA 链
        retriever = Retriever(vector_store=state.vector_store)
        qa_chain = QAChain(retriever=retriever, llm_manager=state.llm_manager)

        # 执行问答
        result = qa_chain.run(message)

        # 格式化响应
        response = result.answer

        # 添加引用
        if result.citations:
            response += "\n\n---\n**📚 来源引用:**\n"
            for citation in result.citations:
                response += f"\n📖 《{citation.book_title}》{citation.chapter_title} (第{citation.page_num}页)\n"

        history.append((message, response))

    except Exception as e:
        error_msg = f"❌ 问答出错: {str(e)}"
        history.append((message, error_msg))

    return history


def create_interface() -> gr.Blocks:
    """创建 Gradio 界面"""

    state = SessionState()

    with gr.Blocks(
        title="Book RAG - 知识库问答",
        analytics_enabled=False,
    ) as app:

        gr.Markdown(
            """
            # 📚 Book RAG - 知识库问答

            上传文档，配置 API Key，开始智能问答！支持 PDF、DOCX、MD、EPUB 格式。
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 配置")

                api_key_input = gr.Textbox(
                    label="OpenRouter API Key",
                    placeholder="输入你的 OpenRouter API Key (sk-or-v1...)",
                    type="password",
                    value="",
                )

                model_dropdown = gr.Dropdown(
                    label="选择模型",
                    choices=MODEL_OPTIONS,
                    value="deepseek",
                )

                gr.Markdown("""
                **使用说明:**
                1. 输入 OpenRouter API Key
                2. 选择 LLM 模型
                3. 上传文档文件
                4. 开始问答
                """)

            with gr.Column(scale=1):
                gr.Markdown("### 📄 文档上传")

                file_upload = gr.File(
                    label="上传文档",
                    file_count="multiple",
                    file_types=[".pdf", ".docx", ".doc", ".md", ".markdown", ".epub"],
                )

                upload_status = gr.Textbox(
                    label="上传状态",
                    lines=5,
                    interactive=False,
                    value="等待上传...",
                )

                upload_btn = gr.Button("📤 上传文档", variant="primary", size="lg")

        gr.Markdown("### 💬 问答")

        chatbot = gr.Chatbot(
            label="对话历史",
            height=400,
        )

        with gr.Row():
            chat_input = gr.Textbox(
                label="输入问题",
                placeholder="输入你的问题...",
                scale=4,
                autofocus=True,
            )
            submit_btn = gr.Button("发送", variant="primary", scale=1, size="lg")

        with gr.Row():
            clear_btn = gr.Button("🗑️ 清空对话", variant="secondary")

        # 示例问题
        gr.Examples(
            examples=[
                "文档的主要内容是什么？",
                "总结一下核心观点",
                "有什么关键结论？",
            ],
            inputs=chat_input,
            label="示例问题",
        )

        # 事件绑定
        def handle_upload(files):
            return process_upload(files, state)

        upload_btn.click(
            fn=handle_upload,
            inputs=[file_upload],
            outputs=[upload_status],
        )

        def handle_chat(message, history, api_key, model):
            return chat_response(message, history, api_key, model, state)

        submit_btn.click(
            fn=handle_chat,
            inputs=[chat_input, chatbot, api_key_input, model_dropdown],
            outputs=[chatbot],
        ).then(
            lambda: "",
            outputs=[chat_input],
        )

        chat_input.submit(
            fn=handle_chat,
            inputs=[chat_input, chatbot, api_key_input, model_dropdown],
            outputs=[chatbot],
        ).then(
            lambda: "",
            outputs=[chat_input],
        )

        clear_btn.click(
            fn=lambda: [],
            outputs=[chatbot],
        )

    return app


if __name__ == "__main__":
    import sys

    print("🚀 Starting Gradio app...", file=sys.stderr, flush=True)
    print("📦 Loading modules...", file=sys.stderr, flush=True)

    app = create_interface()

    print("📱 Interface created, launching...", file=sys.stderr, flush=True)
    print("🌐 Open http://127.0.0.1:7861 in your browser", file=sys.stderr, flush=True)

    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        quiet=False,
    )
