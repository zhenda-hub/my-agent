# my-agent 改造为 book-rag - 待办事项

## 项目概述

基于 my-agent 代码库，增强引用追踪功能，使其更适合图书问答场景。

## 改名方案（可选）

### 方案 1：GitHub 仓库重命名（推荐）

1. 在 GitHub 上重命名仓库：
   - 访问 `https://github.com/yourusername/my-agent/settings`
   - Repository name 改为 `book-rag`

2. 更新本地仓库：
   ```bash
   git remote set-url origin git@github.com:yourusername/book-rag.git
   git push -u origin main
   ```

### 方案 2：仅修改项目名称

修改以下文件中的项目名称：
- `pyproject.toml` - name 字段
- `README.md` - 项目描述
- `src/api/main.py` - API 标题

## 实现步骤

### 第 1 步：更新依赖

**文件**: `pyproject.toml`

```toml
# 新增依赖
litellm = "^1.45.0"        # 多 LLM 支持
ebooklib = "^0.18"         # EPUB 支持
openai = "^1.12.0"         # Openai SDK（可选）
anthropic = "^0.25.0"      # Anthropic SDK（可选）
```

### 第 2 步：扩展 PDF 加载器

**文件**: `src/loaders/pdf_loader.py`

- 在 metadata 中添加 `page_num` 字段（已有，确认是否正确）
- 确保每页文档都有页码信息

### 第 3 步：新增 EPUB 加载器

**文件**: `src/loaders/epub_loader.py`（新建）

```python
from ebooklib import epub
from .base import BaseLoader, Document

class EPUBLoader(BaseLoader):
    def load(self, source: str) -> list[Document]:
        # 1. 解析 EPUB 文件
        # 2. 提取目录结构（TOC）
        # 3. 按章节加载内容
        # 4. 添加章节元数据（chapter_title, chapter_id）
```

### 第 4 步：新增章节检测器

**文件**: `src/chunking/chapter_detector.py`（新建）

```python
class ChapterDetector:
    """章节检测器 - 从文档中提取章节结构"""

    def detect_pdf_chapters(self, pdf_path: str) -> list[dict]:
        # 基于字体大小和位置检测章节标题
        pass

    def detect_epub_chapters(self, epub_path: str) -> list[dict]:
        # 从 EPUB TOC.ncx 提取章节结构
        pass

    def detect_txt_chapters(self, txt_content: str) -> list[dict]:
        # 正则模式匹配：
        # - ^Chapter\s+\d+[:\.\s].*
        # - ^第[一二三四五六七八九十\d]+章.*
        # - ^\d+\.\s+[\w\u4e00-\u9fff]+
        pass
```

### 第 5 步：新增多 LLM 管理器

**文件**: `src/chains/llm_manager.py`（新建）

```python
from litellm import acompletion
import os

class LLMManager:
    """多云 LLM 管理器"""

    def __init__(self):
        self.providers = {
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        }

    async def generate(self, prompt: str, provider: str = "deepseek") -> str:
        model_map = {
            "deepseek": "deepseek/deepseek-chat",
            "openai": "openai/gpt-4",
            "anthropic": "anthropic/claude-3-opus",
        }
        response = await acompletion(
            model=model_map[provider],
            messages=[{"role": "user", "content": prompt}],
            api_key=self.providers[provider]
        )
        return response.choices[0].message.content
```

### 第 6 步：扩展 QA Chain

**文件**: `src/chains/qa_chain.py`

```python
@dataclass
class QAResult:
    answer: str
    sources: list[Source]

    # 新增：详细引用
    citations: list[Citation] = field(default_factory=list)

@dataclass
class Citation:
    """精确引用信息"""
    book_title: str          # 书名
    chapter_title: str       # 章节标题
    page_num: int            # 页码
    excerpt: str             # 引用段落
    confidence: float        # 置信度
```

### 第 7 步：更新 API

**文件**: `src/api/main.py`

```python
@app.post("/api/v1/query")
async def query(request: QueryRequest):
    result = qa_chain.run(request.query)

    return {
        "answer": result.answer,
        "sources": result.sources,
        "citations": result.citations,  # 新增字段
    }
```

### 第 8 步：更新配置

**文件**: `.env`

```bash
# 新增多 LLM 配置
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 第 9 步：测试验证

- [ ] 摄入 PDF 图书，验证页码追踪
- [ ] 摄入 EPUB 图书，验证章节检测
- [ ] 查询测试，验证引用格式正确
- [ ] 切换不同 LLM，验证多云支持

## 关键文件清单

### 需要修改的文件
| 文件 | 修改内容 |
|------|---------|
| `pyproject.toml` | 添加新依赖 |
| `src/loaders/pdf_loader.py` | 确认页码元数据 |
| `src/chains/qa_chain.py` | 添加 Citation 字段 |
| `src/api/main.py` | 返回 citations |
| `.env` | 添加多 LLM API key |

### 需要新建的文件
| 文件 | 功能 |
|------|------|
| `src/loaders/epub_loader.py` | EPUB 加载器 |
| `src/chunking/chapter_detector.py` | 章节检测器 |
| `src/chains/llm_manager.py` | 多 LLM 管理器 |

## 引用格式示例

**中文格式**：
```
根据《三体》第三章"三体问题"（第45页）：
"[引用段落内容]"
```

**英文格式**：
```
According to "The Three-Body Problem", Chapter 3 (page 45):
"[excerpt content]"
```
