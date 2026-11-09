"""
@Time    : 2026/11/5
@Author  : zhujunxiao
@File    : thread_pool_executor

线程池，并行执行示例
"""
import concurrent.futures
import json
import math
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"  # DeepSeek API 端点
)


# ==========================================
# 1. 定义本地真实函数 & 注册表
# ==========================================
def get_weather(location):
    print(f"☁️ [执行工具] 开始查询 {location} 的天气...")
    time.sleep(2.0)  # 模拟 2 秒的网络延迟
    print(f"☁️ [执行工具] 查询完成: {location}")
    return json.dumps({"location": location, "weather": "晴转多云", "temp": "25℃"})


def calculate_sqrt(number):
    print(f"🧮 [执行工具] 开始计算 {number} 的平方根...")
    time.sleep(2.0)  # 模拟 2 秒的计算延迟
    result = math.sqrt(float(number))
    print(f"🧮 [执行工具] 计算完成: {number}")
    return json.dumps({"number": number, "sqrt": result})


# 函数注册表
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculate_sqrt": calculate_sqrt
}

# ==========================================
# 2. 面向大模型的工具描述 (JSON Schema)
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气状况",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "要查询的城市名称，例如北京"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_sqrt",
            "description": "计算一个数字的平方根",
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "number",
                        "description": "需要计算平方根的数字"
                    }
                },
                "required": ["number"]
            }
        }
    }
]


# ==========================================
# 3. 串行 vs 并行 的底层调度实现
# ==========================================
def execute_tools_serial(tool_calls):
    """串行执行：一个接一个排队执行"""
    results = []
    start_time = time.time()

    for tc in tool_calls:
        func_name = tc.function.name
        func_args = json.loads(tc.function.arguments)
        if func_name in TOOL_REGISTRY:
            res = TOOL_REGISTRY[func_name](**func_args)
            results.append({"id": tc.id, "result": res})

    end_time = time.time()
    print(f"⏳ 串行执行总耗时: {end_time - start_time:.2f} 秒")
    return results


def execute_tools_parallel(tool_calls):
    """并行执行：开多线程同时干活"""
    results = []
    start_time = time.time()

    # 定义单个线程要干的活
    def _run_single_tool(tc):
        func_name = tc.function.name
        func_args = json.loads(tc.function.arguments)
        if func_name in TOOL_REGISTRY:
            res = TOOL_REGISTRY[func_name](**func_args)
            return {"id": tc.id, "result": res}
        return None

    # 使用 Python 原生的线程池实现并发调用
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # executor.map 会自动开多线程执行，并且最后收集结果时仍保持原本的顺序
        results = list(executor.map(_run_single_tool, tool_calls))

    end_time = time.time()
    print(f"🚀 并行执行总耗时: {end_time - start_time:.2f} 秒")
    return results


# ==========================================
# 以下是你提供的调用测试代码
# ==========================================
MODEL = "deepseek-chat"  # 替换成你实际可用的模型，比如 "deepseek-chat" 或 "gpt-4o"

print("🤖 发送并行请求给大模型...")
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "帮我查一下北京的天气，同时计算 sqrt(256)"}
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0.7,
    max_tokens=512
)
assistant_msg = response.choices[0].message

if assistant_msg.tool_calls:
    print(f"\n✅ LLM 决定同时调用 {len(assistant_msg.tool_calls)} 个工具：")
    for tc in assistant_msg.tool_calls:
        print(f"  - {tc.function.name} 参数: {tc.function.arguments}")

    print("\n--- 【对比测试开始】 ---")

    print("\n[模式 A] 串行执行（慢）：")
    serial_results = execute_tools_serial(assistant_msg.tool_calls)

    print("\n[模式 B] 并行执行（快）：")
    parallel_results = execute_tools_parallel(assistant_msg.tool_calls)
else:
    print("LLM 直接回答，未调用工具")
