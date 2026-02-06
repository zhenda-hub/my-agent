# 待办事项

## 核心功能 ✅

- [x] 更新 pyproject.toml 添加新依赖
- [x] 创建目录结构
- [x] 实现配置管理 (config.py)
- [x] 实现 Embedding 封装 (embeddings.py)
- [x] 实现文档加载器 (loaders/)
- [x] 实现文档切片逻辑
- [x] 实现向量存储 (vector_store.py)
- [x] 创建文档摄入脚本 (ingest.py)
- [x] 实现 RAG 检索器 (retriever/base.py)
- [x] 实现问答链 (chains/qa_chain.py)
- [x] 支持引用溯源
- [x] 实现 Gradio Web 界面 (web/app.py)

## 优化项

- [ ] 使用 LangChain 内置组件重构
  - [x] 文档加载器 → PyPDFLoader, TextLoader 等
  - [ ] 文本分割器 → RecursiveCharacterTextSplitter
  - [ ] Embedding → SentenceTransformerEmbeddings
  - [ ] 向量存储 → Chroma.from_documents
  - [ ] 问答链 → create_retrieval_chain

## 测试

- [ ] 编写单元测试
- [ ] 测试文档摄入流程
- [ ] 测试问答接口

## 其他

- [ ] 添加日志系统
- [ ] 添加缓存机制
- [x] 添加用户界面（Streamlit）




可以用第三方包替代的功能
  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       当前实现        │               LangChain 内置替代                │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 PDFLoader      │ PyPDFLoader / PDFMinerLoader                    │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 DocxLoader     │ Docx2txtLoader / UnstructuredWordDocumentLoader │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 MarkdownLoader │ TextLoader                                      │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 WebLoader      │ WebLoader / UnstructuredURLLoader               │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 手写 split_text       │ RecursiveCharacterTextSplitter                  │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 Embeddings     │ SentenceTransformerEmbeddings                   │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 VectorStore    │ Chroma.from_documents                           │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 Retriever      │ VectorStoreRetriever                            │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 自定义 QAChain        │ create_retrieval_chain / RetrievalQA            │
  └───────────────────────┴─────────────────────────────────────────────────┘


  