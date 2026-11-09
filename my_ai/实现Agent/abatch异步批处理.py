"""
@Time    : 2026/11/6
@Author  : zhujunxiao
@File    : abatch异步批处理
"""
import asyncio

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)

# 设置并发数为3
config = RunnableConfig(max_concurrency=3)

model = ChatDeepSeek(model="deepseek-v4-pro",
                     #  base_url=os.environ.get("DEEPSEEK_BASE_URL"),
                     max_retries=5,  # 重试次数
                     timeout=120)  # 超时时间


async def main():
    task = asyncio.create_task(
        model.abatch(
            [
                "请介绍下你自己。",
                "请问什么是机器学习？",
                "你知道机器学习和深度学习区别么？",
            ],
            config=config,
        )
    )
    print("继续处理其他事情")

    # 获取任务结果
    # 注意，即使不关心结果，也要执行一下 await task，确保模型任务完成
    # 因为`main()` 结束后，`asyncio.run()` 会关闭事件循环，尚未完成的后台任务可能被取消
    responses = await task

    for response in responses:
        print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
