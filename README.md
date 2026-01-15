# 企业级知识库问答 Agent

基于 RAG（检索增强生成）的企业知识库问答系统，支持多格式文档解析和引用溯源。

## 功能特性

- **多格式文档解析**：支持 PDF、Word、Markdown 格式
- **引用溯源**：显示答案参考来源，支持原文链接跳转
- **语义检索**：基于 Chroma 向量数据库的语义搜索
- **RESTful API**：FastAPI 提供的问答和文档上传接口

## 环境准备

```bash
# 使用 uv 安装依赖（推荐）
uv venv
uv sync
source .venv/bin/activate
```

## 配置

复制 `.env_example` 为 `.env` 并配置：

```bash
# DeepSeek API
DEEPSEEK_API_KEY=your-api-key-here

# 其他配置使用默认值即可
```

## 使用方法

### 1. 摄入文档

将文档放入 `data/documents/` 目录，然后运行：

```bash
uv run python scripts/ingest.py --path data/documents/
```

或摄入单个文件：

```bash
uv run python scripts/ingest.py --path data/documents/example.pdf
```

### 2. 启动 API 服务

```bash
uv run python src/api/main.py
```

### 3. 测试问答接口

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "你的问题"}'
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 信息 |
| `/health` | GET | 健康检查 |
| `/api/v1/query` | POST | 问答接口 |
| `/api/v1/upload` | POST | 上传文档 |
| `/api/v1/stats` | GET | 统计信息 |

## 项目结构

```
my-agent/
├── src/
│   ├── config.py          # 配置管理
│   ├── embeddings.py      # Embedding 封装
│   ├── vector_store.py    # Chroma 向量存储
│   ├── loaders/           # 文档加载器
│   ├── retriever/         # 检索器
│   ├── chains/            # 问答链
│   └── api/               # API 服务
├── scripts/
│   └── ingest.py          # 文档摄入脚本
├── data/
│   ├── documents/         # 待处理文档
│   └── chroma/            # 向量数据库
├── pyproject.toml
├── .env
└── README.md
```
