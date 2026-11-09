"""
@Time    : 2026/11/6
@Author  : zhujunxiao
@File    : ChatOpenAI
"""
# 连接本地vLLM服务
from langchain_openai import ChatOpenAI

# 连接到本地 vLLM 服务,配置长连接池，减少握手开销
model = ChatOpenAI(
    model="qwen-32b-chat",  # 指定使用的模型名称
    base_url="http://localhost:8000/v1",  # vLLM 的 OpenAI API 地址
    api_key="EMPTY",  # vLLM 不验证 key，可以随便写
    max_retries=5,  # 增加重试次数
    timeout=120.0,  # 超时时间设长
    http_client={  # 自定义 HTTP 客户端
        "limits": {
            "max_connections": 100,  # 最大连接数
            "max_keepalive_connections": 20  # 最大保持活动连接数
        }
    }
)
