# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 LangChain 的 Tool-Using Agent 演示项目，展示如何创建一个能够使用工具（计算器）执行任务的 AI Agent。使用 DeepSeek 作为 LLM 提供商。

## 常用命令

```bash
# 使用 uv 安装依赖（推荐）
uv venv          # 创建虚拟环境
uv sync          # 同步依赖
source .venv/bin/activate  # 激活环境

# 运行演示
uv run python demo_agent.py
# 或激活环境后
python demo_agent.py
```

## 架构说明

### 核心组件

1. **Tool Definition (`demo_agent.py:11-16`)**: 自定义计算器工具，使用 `eval()` 执行数学表达式。注意：`eval()` 存在安全风险，仅适用于演示场景。

2. **LLM Integration (`demo_agent.py:29`)**: 通过 `langchain_community.llms.DeepSeek` 集成 DeepSeek API。

3. **Agent Type (`demo_agent.py:35`)**: 使用 `ZERO_SHOT_REACT_DESCRIPTION` agent 类型，这是一种 React 风格的 agent，不需要训练示例即可工作。

### 代码流程

1. 从 `.env` 加载环境变量（`DEEPSEEK_API_KEY`）
2. 定义工具并包装为 LangChain Tool
3. 初始化 DeepSeek LLM（temperature=0 确保确定性输出）
4. 创建 agent 并传入工具和 LLM
5. 执行查询

## 环境配置

项目使用 `.env` 文件管理 API 密钥：

```bash
DEEPSEEK_API_KEY=your-api-key-here
```

参考 `.env_example` 模板。API 密钥配置说明见 README.md。

## 依赖管理

- 使用 `uv` + `pyproject.toml` 管理依赖
- 保留 `req.txt` 作为参考
- 主要依赖：`langchain`、`langchain-community`、`langchain-core`、`python-dotenv`、`pydantic`
- Python 版本要求：>= 3.12
