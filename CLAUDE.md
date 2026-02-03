# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 RAG（检索增强生成）的知识库问答系统，支持多格式文档解析和引用溯源。

## 核心功能

- **多格式文档解析**：支持 PDF、Word、Markdown、EPUB 格式
- **网页抓取**：支持从 URL 抓取网页内容
- **语义检索**：基于 Chroma 向量数据库的语义搜索
- **引用溯源**：显示答案参考来源，包含书名、章节、页码
- **Web 界面**：Gradio 提供的可视化问答界面
- **多云 LLM**：通过 OpenRouter 支持多种模型（DeepSeek、GPT-4、Claude 等）

## 常用命令

```bash
# 使用 uv 安装依赖（推荐）
uv venv          # 创建虚拟环境
uv sync          # 同步依赖
source .venv/bin/activate  # 激活环境

# 运行 Web 界面
uv run python src/web/app.py
# 或激活环境后
python src/web/app.py
```

## 项目结构

```
book-rag/
├── src/
│   ├── config.py          # 配置管理
│   ├── embeddings.py      # Embedding 封装（sentence-transformers）
│   ├── vector_store.py    # Chroma 向量存储
│   ├── loaders/           # 文档加载器
│   │   ├── base.py        # Document 基类和加载器基类
│   │   ├── pdf_loader.py  # PDF 加载器（pypdf + pdfplumber）
│   │   ├── docx_loader.py # Word 加载器
│   │   ├── markdown_loader.py # Markdown 加载器
│   │   ├── epub_loader.py # EPUB 加载器
│   │   └── web_loader.py  # 网页抓取（trafilatura）
│   ├── chunking/          # 文本分块
│   │   └── chapter_detector.py # 章节检测
│   ├── retriever/         # 检索器
│   │   └── base.py        # 基于向量相似度的检索器
│   ├── chains/            # 问答链
│   │   ├── llm_manager.py # LLM 管理器（OpenRouter）
│   │   └── qa_chain.py    # QA 问答链
│   └── web/               # Gradio Web 界面
│       └── app.py         # 主应用入口
├── data/
│   ├── documents/         # 待处理文档
│   └── chroma/            # 向量数据库存储
├── pyproject.toml         # 项目配置和依赖
├── .env_example           # 环境变量模板
└── README.md
```

## 核心组件说明

### 1. 文档加载器 (`src/loaders/`)

所有加载器继承自基类 `BaseLoader`，返回 `Document` 对象列表：

```python
class Document:
    content: str      # 文档内容
    metadata: dict    # 元数据（书名、章节、页码等）
    source: str       # 来源（文件路径或 URL）
```

### 2. 向量存储 (`src/vector_store.py`)

使用 Chroma 作为向量数据库，核心方法：
- `add_documents(documents)` - 添加文档
- `search(query, k=4)` - 语义搜索
- `delete_by_source(source)` - 删除指定来源
- `source_exists(source)` - 检查来源是否存在

### 3. 检索器 (`src/retriever/base.py`)

基于向量相似度的检索器，返回最相关的文档块。

### 4. LLM 管理器 (`src/chains/llm_manager.py`)

- 支持 OpenRouter API
- 动态获取免费模型列表
- 支持多种模型（deepseek、gpt-4、claude 等）

### 5. 问答链 (`src/chains/qa_chain.py`)

结合检索器和 LLM 生成带引用的答案，返回：
- `answer`: 答案文本
- `citations`: 引用列表（书名、章节、页码）

### 6. Web 界面 (`src/web/app.py`)

Gradio 应用，功能：
- 文档上传（支持批量）
- 网页 URL 抓取
- 交互式问答
- 模型选择
- 进度显示

## 环境配置

项目使用 `.env` 文件管理 API 密钥：

```bash
# OpenRouter API Key（必需）
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

参考 `.env_example` 模板。

## 依赖管理

- 使用 `uv` + `pyproject.toml` 管理依赖
- Python 版本要求：>= 3.12
- 主要依赖：
  - `langchain` / `langchain-community` / `langchain-core`
  - `chromadb` - 向量数据库
  - `sentence-transformers` - Embeddings
  - `gradio` - Web 界面
  - `openai` - OpenRouter API
  - 文档解析：`pypdf`、`pdfplumber`、`python-docx`、`ebooklib`、`trafilatura`

## 数据流程

1. **文档加载**: 使用对应加载器解析文档，提取文本和元数据
2. **文本切分**: 按章节或固定大小切分文本块
3. **向量化**: 使用 sentence-transformers 生成 embeddings
4. **存储**: 存入 Chroma 向量数据库
5. **检索**: 根据问题进行语义搜索
6. **生成**: LLM 基于检索结果生成带引用的答案

## 软件开发流程

### 分支管理 - Worktree

编码前必须使用 `git worktree` 创建独立的工作目录：

```bash
# 创建新的 worktree 分支
git worktree add ../book-rag-<feature-name> -b feature/<feature-name>

# 进入 worktree 目录
cd ../book-rag-<feature-name>

# 开发完成后，删除 worktree
git worktree remove ../book-rag-<feature-name>
```

**命名规范**:
- 功能分支: `feature/xxx`
- 修复分支: `fix/xxx`
- 重构分支: `refactor/xxx`

### TDD 开发流程

采用测试驱动开发（TDD）：

1. **Red**: 先编写失败的测试
   ```bash
   # 创建测试文件
   # tests/test_<module>.py
   uv run pytest tests/test_<module>.py -v  # 确认测试失败
   ```

2. **Green**: 编写最小代码使测试通过

3. **Refactor**: 重构代码，保持测试通过

### 代码设计原则

#### 1. SOLID 原则

- **单一职责（SRP）**: 每个模块只负责一个功能
- **开闭原则（OCP）**: 对扩展开放，对修改封闭
- **里氏替换（LSP）**: 子类可替换父类
- **接口隔离（ISP）**: 接口小而专注
- **依赖倒置（DIP）**: 依赖抽象而非具体实现

#### 2. 项目特定原则

- **加载器可扩展性**: 新增文档格式只需添加新的加载器类，无需修改现有代码
- **向量存储抽象**: `vector_store.py` 提供统一接口，可替换底层向量数据库
- **LLM 可替换性**: 通过 `LLMManager` 统一管理，支持切换不同的 LLM 提供商
- **错误处理**: 外部依赖（API、文件解析）必须有异常处理
- **类型注解**: 所有公共函数必须包含类型注解

#### 3. 代码风格

- 使用 `pydantic.BaseModel` 定义数据模型
- 优先使用组合而非继承
- 避免全局变量，使用依赖注入
- 函数长度不超过 50 行
- 类文件不超过 300 行

### 测试规范

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_pdf_loader.py -v

# 运行特定测试函数
uv run pytest tests/test_pdf_loader.py::test_load_document -v

# 查看覆盖率
uv run pytest --cov=src --cov-report=html
```

测试文件结构：
```
tests/
├── test_loaders/      # 加载器测试
├── test_chains/       # 问答链测试
├── test_retriever/    # 检索器测试
└── fixtures/          # 测试数据
```

### 提交规范

使用约定式提交：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `refactor`: 重构
- `test`: 添加测试
- `docs`: 文档更新
- `chore`: 构建/工具变更

**示例**:
```
feat(loaders): 添加 TXT 文档加载器支持

- 新增 TextLoader 类
- 支持自动编码检测
- 添加单元测试

Closes #123
```

## 开发注意事项

1. **添加新文档格式**: 在 `src/loaders/` 下创建新的加载器，继承 `BaseLoader`
2. **修改切分策略**: 修改 `src/web/app.py` 中的 `split_text` 函数
3. **更换 Embedding 模型**: 修改 `src/embeddings.py`
4. **更换向量数据库**: 修改 `src/vector_store.py`
5. **自定义 prompt**: 修改 `src/chains/qa_chain.py`
