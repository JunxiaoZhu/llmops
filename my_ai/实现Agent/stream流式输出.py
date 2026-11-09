"""
@Time    : 2026/11/7
@Author  : zhujunxiao
@File    : stream流式输出
"""

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)

model = ChatDeepSeek(model="deepseek-v4-pro",
                     #  base_url=os.environ.get("DEEPSEEK_BASE_URL"),
                     max_retries=5,  # 重试次数
                     timeout=120)  # 超时时间

# 使用.stream()方法进行流式传输
for chunk in model.stream("用一段话描述大海。", stream_mode="values"):
    # print 默认会在输出末尾加\n，设置 end="" 后，末尾不再追加任何字符
    # 默认内容先写入缓冲区，等缓冲区满了或程序结束才真正显示到终端，flush=True 强制在立即把缓冲区内容刷到终端
    print(chunk.content, end="", flush=True)

# 输出会像真正的打字效果一样，一个一个词地出现。
