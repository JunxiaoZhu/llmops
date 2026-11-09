"""
@Time    : 2026/11/8
@Author  : zhujunxiao
@File    : 自定义tool
"""
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

load_dotenv(override=True)


# 1. 定义一个简单的 Tool (Runnable)
@tool
def multiply(a: int, b: int) -> int:
    return a * b


# 2.导入模型
model = init_chat_model(model="deepseek-v4-pro", model_provider="deepseek", )

# 3.创建Agent
agent = create_agent(model=model, tools=[multiply])

# agent运行配置
config = {
    "configurable": {"thread_id": "limit_demo"},  # thread_id 线程ID
    # 限制Agent图最多执行 4 个步骤，对应的图步骤：
    # 1	初始化 Agent 状态
    # 2	第一次调用模型，决定调用工具
    # 3	执行 multiply 工具
    # 4	第二次调用模型，生成最终答案
    "recursion_limit": 4
}

# 4. 调用Agent
response = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "帮我计算12乘以6等于多少？"
    }]
}, config=config)

print(response)
print(response["messages"])
# 最后一条通常是 Agent 的最终回答
print(response["messages"][-1].content_blocks)
