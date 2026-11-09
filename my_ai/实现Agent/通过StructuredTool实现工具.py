"""
@Time    : 2026/11/8
@Author  : zhujunxiao
@File    : 通过StructuredTool实现工具
"""
import asyncio
from typing import Type

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import StructuredTool
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field

load_dotenv(override=True)


# 1. 定义包含业务逻辑的工具
class OrderQueryInput(BaseModel):
    """订单查询参数"""
    order_id: str = Field(description="订单编号，格式：ORD-2024-XXXX")
    include_details: bool = Field(default=False, description="是否包含商品明细")


class OrderQueryTool(StructuredTool):
    """订单查询工具"""
    name: str = "query_order"
    description: str = "查询电商平台订单状态和物流信息"
    args_schema: Type[BaseModel] = OrderQueryInput
    return_direct: bool = False

    def _run(self, order_id: str, include_details: bool = False) -> dict:
        # 模拟数据库查询
        order_db = {
            "ORD-2024-1234": {"status": "已发货", "express": "顺丰", "amount": 299},
            "ORD-2024-5678": {"status": "待付款", "express": "", "amount": 149},
        }

        # 处理查询逻辑
        if order_id not in order_db:
            return {"error": f"订单 {order_id} 不存在"}
        result = order_db[order_id]

        # 处理包含明细的情况
        if include_details:
            result["items"] = ["商品A × 2", "商品B × 1"]

        return result


# 2. 初始化模型
model = ChatDeepSeek(model="deepseek-v4-pro")  # 超时时间

# 3. 创建 ReAct Agent（自动处理工具调用）
agent = create_agent(
    model=model,
    tools=[OrderQueryTool()],  # 直接传入 StructuredTool 实例
    system_prompt="你是一个电商客服助手，使用工具查询订单信息，回答要友好且准确",
    checkpointer=InMemorySaver()
)


# 4. 执行并观察 ReAct 过程
async def run_agent():
    config = {"configurable": {"thread_id": "customer_001"}, "recursion_limit": 15}  # 最大 15 次迭代

    query = "请帮我查订单 ORD-2024-1234 的详细状态，包括商品明细"

    async for step in agent.astream(
            {"messages": [{"role": "user", "content": query}]},
            config=config,
            # 返回每一步的完整状态：随着图执行，逐步返回，不是逐段输出模型生成的文字。
            stream_mode="values"
    ):
        message = step["messages"][-1]
        # pretty_print() 美化输出
        message.pretty_print()
        print("-" * 50)


# 运行
if __name__ == "__main__":
    asyncio.run(run_agent())
