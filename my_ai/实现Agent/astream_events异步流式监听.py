"""
@Time    : 2026/11/7
@Author  : zhujunxiao
@File    : astream_events异步流式监听
"""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


# 无论从哪个工作目录启动，都加载 llmops-api/.env。
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)


prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的 AI 助手。"),
    ("human", "{question}"),
])

# DeepSeek 提供 OpenAI 兼容接口，因此使用 ChatOpenAI，并显式传入
# DEEPSEEK_* 配置，避免 ChatOpenAI 误读 OPENAI_* 配置。
llm = ChatOpenAI(
    model="deepseek-v4-pro",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ["DEEPSEEK_BASE_URL"],
    max_retries=5,
    timeout=120,
)

chain = prompt | llm


async def consume_events() -> None:
    """遍历链路产生的语义事件。"""
    async for event in chain.astream_events(
        {"question": "请用一句话介绍一下 LangChain 1.0 的核心思想。"},
        version="v2",
    ):
        print(f"[Event] type={event['event']}")
        if event.get("data"):
            print("   data:", event["data"])
        print("-----------------------------")


async def main() -> None:
    # create_task() 接收协程，因此先把 async for 封装在 consume_events() 中。
    event_task = asyncio.create_task(consume_events())

    # 任务已经提交，主协程可以继续执行其他代码。
    print("事件监听任务已启动，主协程继续执行其他代码。")
    await asyncio.sleep(0)

    # 进程退出前等待监听任务结束，避免未完成的请求被取消。
    await event_task


if __name__ == "__main__":
    asyncio.run(main())
