"""通过 stdio MCP 数学工具和本地天气工具运行 Agent。"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)
script_dir = Path(__file__).resolve().parent


@tool
def get_weather(city: str) -> str:
    """查询指定城市的模拟天气数据（非实时天气）。"""
    weather_data = {
        "北京": "晴朗，气温25°C",
        "上海": "多云，气温28°C",
        "广州": "小雨，气温30°C",
    }
    return f"{city}的天气是：{weather_data.get(city, '未知')}"


async def main():
    # 初始化MCP客户端
    mcp_client = MultiServerMCPClient({
        "math1": {
            "transport": "stdio",  # stdio本地 / http远程（下面两个参数就不需要了，配置url即可）
            "command": sys.executable,  # 指定用当前的解释器，启动MCP服务器子进程（等同于在命令行执行：python ..../mcp_服务器_提供方法.py）
            "args": [str(script_dir / "mcp_服务器_提供方法.py")],  # 这里要用绝对路径
        }
    })
    # 加载失败时直接报错，避免 MCP 连接失败却被误认为演示成功。
    mcp_tools = await mcp_client.get_tools()
    print(f"成功加载 MCP 工具：{[t.name for t in mcp_tools]}")

    llm = ChatDeepSeek(model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    agent = create_agent(
        model=llm,
        tools=[get_weather, *mcp_tools],
        system_prompt=(
            "你是一个多功能助手。使用天气工具查询模拟天气，"
            "使用 subtract 工具计算温差，不要编造实时天气。"
        ),
    )

    response = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "查询一下北京和上海气温，并且计算一下北京的温度比上海低多少度？",
        }]
    })
    # 展示实际调用的工具，便于确认 MCP 数学工具确实参与了计算。
    for message in response["messages"]:
        if message.type == "tool":
            print(f"工具 {message.name}：{message.content}")
    print(f"Agent: {response['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
