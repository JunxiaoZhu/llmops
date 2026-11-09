"""
@Time    : 2026/11/6
@Author  : zhujunxiao
@File    : batch批处理
"""
import time
from datetime import datetime

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)

# 记录开始时间
start_time = time.time()
print(f"⏱️  开始时间: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

model = ChatDeepSeek(model="deepseek-v4-pro",
                     #  base_url=os.environ.get("DEEPSEEK_BASE_URL"),
                     max_retries=5,  # 重试次数
                     timeout=120)  # 超时时间
# 批量提问
responses = model.batch([
    "请介绍下你自己。",
    "请问什么是机器学习？",
    "你知道机器学习和深度学习区别么？"
], config={"max_concurrency": 3})

# 记录结束时间
end_time = time.time()
total_duration = end_time - start_time

print(f"⏱️  结束时间: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
print(f"📊 总耗时: {total_duration:.2f}s")

# for response in responses:
#   print(response)

for response in model.batch_as_completed([
    "请介绍下你自己。",
    "请问什么是机器学习？",
    "你知道机器学习和深度学习区别么？"
]):
    print(response)
