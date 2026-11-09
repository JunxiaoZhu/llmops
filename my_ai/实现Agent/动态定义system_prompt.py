"""
@Time    : 2026/11/9
@Author  : zhujunxiao
@File    : 动态定义system_prompt
"""
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt

load_dotenv()


@dynamic_prompt
def role_based_prompt(request):
    # request.runtime 运行时对象； 取键为 user_role 的值，不存在，则返回 user；
    user_role = request.runtime.context.get("user_role", "user")

    if user_role == "expert":
        return "你是一个专业气象分析师，提供详细数据"
    elif user_role == "beginner":
        return "你是一个友善的导游，用简单语言解释"
    else:
        return "你是一个简洁的天气助手"


agent = create_agent(
    model="deepseek-chat",
    middleware=[role_based_prompt]  # 注入动态提示
)
response = agent.invoke(
    {"messages": [{"role": "user", "content": "你是谁"}]},
    context={"user_role": "expert"}
)
print(response['messages'][-1].content)
