"""文档管理组件"""
import streamlit as st
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.vector_store import VectorStore


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
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


def render_document_panel(vector_store: "VectorStore") -> None:
    """渲染文档上传面板

    Args:
        vector_store: 向量存储实例
    """
    with st.expander("📄 上传文档", expanded=True):
        uploaded_files = st.file_uploader(
            "选择文件",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt', 'md', 'epub'],
            help="支持：PDF, DOCX, TXT, MD, EPUB"
        )

        if uploaded_files and st.button("上传", type="primary", use_container_width=True):
            with st.status("正在处理...", expanded=True) as status:
                from src.loaders import get_loader
                from src.loaders.base import Document

                total = len(uploaded_files)
                for i, file in enumerate(uploaded_files):
                    status.update(label=f"处理 {file.name} ({i+1}/{total})")

                    # 保存临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as f:
                        f.write(file.getvalue())
                        temp_path = f.name

                    try:
                        path = Path(temp_path)

                        # 检查是否已存在
                        if vector_store.source_exists(str(path)):
                            st.info(f"⏭️ {file.name} 已存在，跳过")
                            continue

                        # 加载文档
                        loader = get_loader(str(path))
                        documents = loader.load(str(path))

                        # 切分文档
                        chunked_docs = []
                        for doc in documents:
                            chunks = split_text(doc.content)
                            for j, chunk in enumerate(chunks):
                                chunked_doc = Document(
                                    content=chunk,
                                    metadata={
                                        **doc.metadata,
                                        "chunk_index": j,
                                        "total_chunks": len(chunks),
                                    },
                                    source=doc.source,
                                )
                                chunked_docs.append(chunked_doc)

                        # 清除旧数据
                        vector_store.delete_by_source(str(path))

                        # 存储到向量库
                        vector_store.add_documents(chunked_docs)
                        st.success(f"✅ {file.name}: {len(chunked_docs)} 个块")

                    except Exception as e:
                        st.error(f"❌ {file.name}: {e}")

                status.update(label="完成！", state="complete")
                st.session_state.documents_loaded = True
                st.rerun()


def render_web_scraping(vector_store: "VectorStore") -> None:
    """渲染网页抓取面板

    Args:
        vector_store: 向量存储实例
    """
    with st.expander("🔗 网页抓取"):
        url = st.text_input("网页 URL", placeholder="https://example.com", key="web_url")

        if st.button("抓取", use_container_width=True, key="scrape_btn"):
            if url and url.strip():
                url = url.strip()

                # 检查是否已存在
                if vector_store.source_exists(url):
                    st.warning(f"⏭️ URL 已存在: {url}")
                    return

                with st.spinner("正在抓取..."):
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
                        vector_store.add_documents(chunked_docs)

                        st.success(f"✅ 成功抓取：{url}\n📊 共 {len(chunked_docs)} 个文档块")
                        st.session_state.documents_loaded = True
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 抓取失败：{e}")


def render_file_management(vector_store: "VectorStore") -> None:
    """渲染文件管理面板

    Args:
        vector_store: 向量存储实例
    """
    with st.expander("📁 文件管理"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("刷新列表", use_container_width=True):
                st.rerun()

        with col2:
            files_count = len(vector_store.get_all_sources())
            st.metric("文件数量", files_count)

        all_sources = vector_store.get_all_sources()
        filenames = [Path(src).name for src in all_sources]

        if filenames:
            selected = st.multiselect(
                "选择用于 RAG 的文件",
                options=filenames,
                default=filenames,
                help="取消选择可从 RAG 中排除"
            )

            # 更新选中的文件
            filename_to_source = {Path(src).name: src for src in all_sources}
            st.session_state.selected_sources = [
                filename_to_source[name] for name in selected
            ]
        else:
            st.info("暂无文件，请先上传文档或抓取网页")
