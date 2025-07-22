# LangChain Tool-Using Agent 演示

## 环境准备

1. 创建虚拟环境:
```bash
python -m venv venv
```

2. 激活虚拟环境:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

3. 安装依赖:
```bash
pip install langchain deepseek
```

## 设置DeepSeek API密钥

1. 编辑.env文件，填写您的API密钥：
```bash
DEEPSEEK_API_KEY=your-api-key-here
```

2. 或者通过命令行设置：
### Linux/Mac
```bash
echo 'DEEPSEEK_API_KEY="your-api-key-here"' > .env
```

### Windows (CMD)
```cmd
echo DEEPSEEK_API_KEY=your-api-key-here > .env
```

### Windows (PowerShell)
```powershell
"`"DEEPSEEK_API_KEY=your-api-key-here`"" | Out-File -FilePath .env -Encoding ASCII
```

## 运行演示
```bash
python demo_agent.py
```

## 项目结构
- `demo_agent.py` - 主程序
- `.gitignore` - Git忽略规则
- `README.md` - 使用说明
