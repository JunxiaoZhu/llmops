"""
@Time    : 2026/11/6
@Author  : zhujunxiao
@File    : 标准化内容块ContentBlocks
"""
import os

from dotenv import load_dotenv
# 1. 定义带速率限制的load_chat_model函数
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)

# 2. 配置速率限制器
rate_limiter = InMemoryRateLimiter(
    requests_per_second=5,  # 每秒最多5个请求
    check_every_n_seconds=1.0  # 每1秒检查一次是否超过速率限制
)


# 3. 对模型调用进行封装，后续直接调用传参数就行
def load_chat_model(
        model: str,
        provider: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        base_url: str | None = os.environ.get("DEEPSEEK_BASE_URL"),
):
    return init_chat_model(
        model=model,  # 模型名称
        model_provider=provider,  # 模型供应商
        temperature=temperature,  # 温度参数，用于控制模型的随机性，值越小则随机性越小
        max_tokens=max_tokens,  # 最大生成token数
        base_url=base_url,  # 专用于自定义 API Server 或代理
        rate_limiter=rate_limiter  # 自动限速
    )


# 加载 DeepSeek 提供的推理模型 deepseek-reasoner
deepseek_model = load_chat_model(
    model="deepseek-v4-pro",  # 指定模型名称
    provider="deepseek"  # 指定模型提供商
)

# 调用模型
res = deepseek_model.invoke("请介绍一下你自己")

# 输出模型返回的结果
print(res)

# 从模型返回的结果中提取内容块
print(res.content_blocks)

llm = ChatDeepSeek(model="deepseek-v4-pro",
                   #  base_url=os.environ.get("DEEPSEEK_BASE_URL"),
                   max_retries=5,  # 重试次数
                   timeout=120)  # 超时时间
rep = llm.invoke("今天长沙的天气怎么样")  # 没有联网功能情况下，无法获取天气

print(rep)
