# 测试说明

本目录包含项目的测试用例。

## 测试文件

### test_llm.py
测试 LLM API 调用功能。

**前置条件：** 需要设置 `OPENROUTER_API_KEY` 环境变量

```bash
# 运行测试
uv run python tests/test_llm.py
```

### test_skip_uploaded.py
测试跳过已上传文件的功能。

```bash
# 运行测试
uv run python tests/test_skip_uploaded.py
```

## 运行所有测试

```bash
# 运行 LLM 测试
uv run python tests/test_llm.py

# 运行跳过上传测试
uv run python tests/test_skip_uploaded.py
```
