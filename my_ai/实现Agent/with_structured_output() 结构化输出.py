"""
@Time    : 2026/11/7
@Author  : zhujunxiao
@File    : with_structured_output() 结构化输出
"""
from typing import List, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field

load_dotenv(override=True)


# 1. 定义期望的输出结构
class Person(BaseModel):
    age: int = Field(ge=0, le=150, description="人的年龄")  # 限制范围 0-150
    # Optional[int] 表示要么是 int 类型，要么是 None，等价于 Union[int, None]
    high: Optional[int] = Field(default=None, description="人的身高")
    hobbies: List[str] = Field(description="人的爱好列表")


llm = ChatDeepSeek(model="deepseek-chat")
# include_raw=True，最终输出会保留原始响应，打印更多内容
# structured_llm = llm.with_structured_output(Person, include_raw=True)
structured_llm = llm.with_structured_output(Person)
result = structured_llm.invoke("提取名为约翰的人的信息，提取不到的数据就为空值。他30岁，喜欢阅读、学习。")

print(f"Result object: {result}")

# 智能体，实现结构化输出
agent = create_agent(
    model=llm,  # 加载的模型
    tools=[],  # 工具列表，这里为空
    response_format=Person  # 指定结构化输出格式
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "提取名为约翰的人的信息，提取不到的数据就为空值。他999岁，喜欢阅读、学习。"
    }]
})

# 由于提取到的年龄是999岁，不符合定义的限制范围，所以：
# 1. 捕获ValidationError
# 2. 在ToolMessage中反馈错误详情
# 3. 让模型重新生成，最终返回合法值150
print(result)
forecast = result["structured_response"]
print(forecast)
