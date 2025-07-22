from langchain.agents import AgentType, initialize_agent
from langchain_community.llms import DeepSeek
from langchain.tools import Tool
from dotenv import load_dotenv
import os

load_dotenv()


# 定义一个简单的计算工具
def calculate(expression):
    """计算数学表达式"""
    try:
        return str(eval(expression))
    except Exception:
        return "计算错误"


# 创建工具
tools = [
    Tool(
        name="Calculator",
        func=calculate,
        description="用于计算数学表达式"
    )
]

# 初始化LLM
llm = DeepSeek(api_key=os.getenv("DEEPSEEK_API_KEY"), temperature=0)

# 创建Agent
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 演示Agent使用工具
print("=== 演示Tool-Using Agent ===")
print(agent.run("计算123乘以456等于多少？"))
print(agent.run("北京现在的天气怎么样？"))
