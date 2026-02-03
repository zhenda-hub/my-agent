"""Gradio Web 界面 - Book RAG"""
import gradio as gr
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


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
        self.current_citations: List = []  # 当前问答的引用列表
        self.selected_sources: List[str] = []  # 用户选中的文件来源

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


def get_initial_models() -> list:
    """
    获取初始模型列表（从 OpenRouter API 动态获取免费模型）

    Returns:
        模型 ID 列表
    """
    import os
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    try:
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if api_key:
            from src.chains.llm_manager import LLMManager
            llm = LLMManager(api_key=api_key)
            models = llm.get_free_models()
            if models:
                return models
    except Exception as e:
        print(f"获取模型列表失败: {e}", file=sys.stderr)

    # 降级到默认模型
    return ["deepseek"]


def process_upload(files: List, state: SessionState, progress: gr.Progress = gr.Progress()) -> str:
    """处理文件上传 - 支持流式进度显示，跳过已上传的文件"""
    if not files:
        return "❌ 请选择文件"

    count = 0
    skipped = 0
    total_chunks = 0
    status_lines = []

    from src.loaders import get_loader
    from src.loaders.base import Document

    # 统计需要处理的文件数量
    files_to_process = []
    skipped_files = []

    for file in files:
        file_path = file.name
        path = Path(file_path)
        if state.vector_store.source_exists(str(path)):
            skipped_files.append(path.name)
        else:
            files_to_process.append(file)

    total_steps = len(files_to_process) * 3  # 每个文件3步：解析、切分、embedding
    current_step = 0

    # 先报告跳过的文件
    if skipped_files:
        status_lines.append(f"⏭️ 跳过 {len(skipped_files)} 个已上传的文件: {', '.join(skipped_files)}")
        skipped = len(skipped_files)

    for file_idx, file in enumerate(files_to_process, 1):
        file_path = file.name
        path = Path(file_path)

        try:
            # 步骤1: 解析文档
            current_step += 1
            progress(current_step / total_steps, desc=f"📖 [{file_idx}/{len(files_to_process)}] 正在解析 {path.name}...")

            loader = get_loader(str(path))
            documents = loader.load(str(path))

            status_lines.append(f"📖 [{file_idx}/{len(files_to_process)}] {path.name}: 已提取 {len(documents)} 页")

            # 步骤2: 切分文档
            current_step += 1
            progress(current_step / total_steps, desc=f"✂️ [{file_idx}/{len(files_to_process)}] 正在切分 {path.name}...")

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

            status_lines.append(f"✂️ [{file_idx}/{len(files_to_process)}] {path.name}: 已切分 {len(chunked_docs)} 块")

            # 清除旧数据
            state.vector_store.delete_by_source(str(path))

            # 步骤3: 生成 embeddings
            current_step += 1
            progress(current_step / total_steps, desc=f"🔢 [{file_idx}/{len(files_to_process)}] 正在生成 embeddings ({len(chunked_docs)} 块)...")

            state.vector_store.add_documents(chunked_docs)

            status_lines.append(f"✅ [{file_idx}/{len(files_to_process)}] {path.name}: 完成！共 {len(chunked_docs)} 个块")
            count += 1
            total_chunks += len(chunked_docs)

        except Exception as e:
            status_lines.append(f"❌ [{file_idx}/{len(files_to_process)}] {path.name}: {str(e)}")

    state.documents_loaded = count > 0 or skipped > 0

    total_processed = count + skipped
    summary = f"📊 共 {total_processed} 个文件 (新增 {count} 个，跳过 {skipped} 个已存在)，共 {total_chunks} 个文档块\n\n" + "\n".join(status_lines)
    return summary


def process_url(url: str, state: SessionState) -> str:
    """处理 URL 抓取"""
    if not url or not url.strip():
        return "❌ 请输入 URL"

    url = url.strip()

    # 检查是否已存在
    if state.vector_store.source_exists(url):
        return f"⏭️ URL 已存在: {url}"

    try:
        from src.loaders.web_loader import WebLoader
        from src.loaders.base import Document

        # 抓取网页
        loader = WebLoader()
        documents = loader.load(url)

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

        # 存储到向量库
        state.vector_store.add_documents(chunked_docs)
        state.documents_loaded = True

        return f"✅ 成功抓取: {url}\n📊 共 {len(chunked_docs)} 个文档块"

    except Exception as e:
        return f"❌ 抓取失败: {url}\n错误: {str(e)}"


def refresh_file_list(state: SessionState) -> Tuple[List[str], str]:
    """
    刷新文件列表 - 从数据库获取所有已上传的文件

    Returns:
        (文件名列表, 信息文本)
    """
    all_sources = state.vector_store.get_all_sources()

    # 提取文件名（从完整路径）
    filenames = [Path(src).name for src in all_sources]

    # 默认全选
    state.selected_sources = all_sources

    info = f"📁 数据库中共有 {len(all_sources)} 个文件"
    return filenames, info


def update_selected_sources(selected_filenames: List[str], state: SessionState) -> None:
    """
    更新用户选中的文件

    Args:
        selected_filenames: 用户在界面上选中的文件名列表
        state: 会话状态
    """
    all_sources = state.vector_store.get_all_sources()

    # 将文件名映射回完整路径
    filename_to_source = {Path(src).name: src for src in all_sources}

    # 更新选中的 sources
    state.selected_sources = [
        filename_to_source[name] for name in selected_filenames
        if name in filename_to_source
    ]


def chat_response(
    message: str,
    history: List[dict],
    api_key: str,
    model: str,
    state: SessionState,
) -> List[dict]:
    """处理问答 - 返回 messages 格式"""
    if not message.strip():
        return history

    # 检查 API Key
    if not api_key:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "⚠️ 请先配置 OpenRouter API Key"})
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
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "⚠️ 请先上传文档"})
        return history

    try:
        from src.chains.qa_chain import QAChain
        from src.retriever.base import Retriever

        # 创建检索器时添加 source 过滤
        filter_dict = None
        if state.selected_sources:
            filter_dict = {"source": {"$in": state.selected_sources}}

        retriever = Retriever(
            vector_store=state.vector_store,
            filter_metadata=filter_dict
        )
        qa_chain = QAChain(retriever=retriever, llm_manager=state.llm_manager)

        # 执行问答
        result = qa_chain.run(message)

        # 保存引用到状态中
        state.current_citations = result.citations

        # 直接使用格式化后的答案（包含引用内容）
        response = result.answer

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

    except Exception as e:
        error_msg = f"❌ 问答出错: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})

    return history


def create_interface() -> gr.Blocks:
    """创建 Gradio 界面"""
    state = SessionState()

    # 启动时获取免费模型列表
    initial_models = get_initial_models()

    with gr.Blocks(
        title="Book RAG - 知识库问答",
        analytics_enabled=False,
    ) as app:

        gr.Markdown(
            """
            # 📚 Book RAG - 知识库问答

            上传文档，配置 API Key，开始智能问答！支持 PDF、DOCX、TXT、MD、EPUB 格式。
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
                    choices=initial_models,
                    value=initial_models[0] if initial_models else "deepseek",
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
                    file_types=[".pdf", ".docx", ".doc", ".txt", ".md", ".markdown", ".epub"],
                )

                upload_status = gr.Textbox(
                    label="上传状态",
                    lines=5,
                    interactive=False,
                    value="等待上传...",
                )

                upload_btn = gr.Button("📤 上传文档", variant="primary", size="lg")

                gr.Markdown("---")

                gr.Markdown("### 🌐 网页抓取")

                url_input = gr.Textbox(
                    label="网页 URL",
                    placeholder="输入网址，如 https://example.com",
                )

                url_status = gr.Textbox(
                    label="抓取状态",
                    lines=3,
                    interactive=False,
                    value="等待输入...",
                )

                url_btn = gr.Button("🔗 抓取网页", variant="secondary", size="lg")

        gr.Markdown("### 📁 已上传文件")

        with gr.Row():
            file_list_info = gr.Textbox(
                label="文件列表",
                value="点击刷新查看文件...",
                interactive=False,
                scale=3
            )
            refresh_files_btn = gr.Button("🔄 刷新", scale=1)

        file_checkbox = gr.CheckboxGroup(
            label="选择用于 RAG 的文件（未选择=使用所有文件）",
            choices=[],
            value=[],
        )

        gr.Markdown("### 💬 问答")

        chatbot = gr.Chatbot(
            label="对话历史",
            height=400,
            sanitize_html=False,  # 允许 HTML 标签（用于可折叠引用）
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
        # 定义处理函数
        def handle_upload(files):
            return process_upload(files, state)

        def handle_url(url):
            return process_url(url, state)

        # 刷新文件列表
        def handle_refresh():
            filenames, info = refresh_file_list(state)
            return filenames, info, filenames

        # 更新选中文件
        def handle_file_selection(selected_filenames):
            update_selected_sources(selected_filenames, state)
            return None

        # 上传后自动刷新文件列表
        upload_btn.click(
            fn=handle_upload,
            inputs=[file_upload],
            outputs=[upload_status],
        ).then(
            fn=handle_refresh,
            inputs=[],
            outputs=[file_checkbox, file_list_info, file_checkbox],
        )

        # URL 抓取后自动刷新文件列表
        url_btn.click(
            fn=handle_url,
            inputs=[url_input],
            outputs=[url_status],
        ).then(
            fn=handle_refresh,
            inputs=[],
            outputs=[file_checkbox, file_list_info, file_checkbox],
        ).then(
            lambda: "",
            outputs=[url_input],
        )

        # 刷新文件列表按钮
        refresh_files_btn.click(
            fn=handle_refresh,
            inputs=[],
            outputs=[file_checkbox, file_list_info, file_checkbox],
        )

        # 文件选择变化
        file_checkbox.change(
            fn=handle_file_selection,
            inputs=[file_checkbox],
            outputs=[],
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
