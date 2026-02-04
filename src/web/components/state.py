"""Streamlit 会话状态管理"""
import streamlit as st


def init_session_state() -> None:
    """初始化会话状态"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = 'deepseek'
    if 'llm_manager' not in st.session_state:
        st.session_state.llm_manager = None
    if 'selected_sources' not in st.session_state:
        st.session_state.selected_sources = []
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False


@st.cache_resource
def get_vector_store_cached():
    """缓存向量存储实例"""
    from src.vector_store import get_vector_store
    return get_vector_store()


@st.cache_resource
def get_embeddings_cached():
    """缓存嵌入模型实例"""
    from src.embeddings import get_embeddings
    return get_embeddings()
