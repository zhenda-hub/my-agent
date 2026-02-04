"""Streamlit Web 界面 - Book RAG"""
import streamlit as st
from src.web.components.state import init_session_state, get_vector_store
from src.web.components.config import render_config_panel
from src.web.components.documents import render_document_panel, render_web_scraping, render_file_management
from src.web.components.chat import render_chat_interface


def main():
    # 页面配置
    st.set_page_config(
        page_title="Book RAG",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 初始化状态
    init_session_state()

    # 侧边栏
    with st.sidebar:
        st.title("📚 Book RAG")
        st.markdown("---")

        render_config_panel()
        st.markdown("---")

        # 获取向量存储（在需要时才加载）
        vector_store = get_vector_store()

        render_document_panel(vector_store)
        st.markdown("")

        render_web_scraping(vector_store)
        st.markdown("---")

        render_file_management(vector_store)

    # 主内容区
    vector_store = get_vector_store()
    render_chat_interface(vector_store)


if __name__ == "__main__":
    main()
