"""
@Time    : 2026/11/5
@Author  : zhujunxiao
@File    : function_calling

工具调用
生产环境部署使用时，需要考虑工具接口超时、入参检查等问题
"""

import os

import math
from dotenv import load_dotenv
from flask import json
from openai import OpenAI

# 强制让 .env 文件里的变量值，覆盖掉系统里已经存在的同名环境变量
load_dotenv(override=True)

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def function_calling_pipeline(
        user_message: str,
        tools: list,
        tool_registry: dict,
        system_prompt: str = "你是一个有用的助手。",
        model: str = "deepseek-chat",
        verbose: bool = True
) -> str:
    """
    完整的 Function Calling 管线（单轮工具调用）

    参数：
        user_message: 用户输入
        tools: 工具定义列表（JSON Schema）
        tool_registry: 工具名称到函数的映射字典
        system_prompt: 系统提示词
        model: 模型名称
        verbose: 是否打印中间过程

    返回：
        LLM 的最终回答文本
    """
    # 步骤 1：构建消息历史
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # 步骤 2-3：发送请求，获取 LLM 决策
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.7,
        max_tokens=2048
    )
    assistant_message = response.choices[0].message

    # 如果 LLM 不需要调用工具，直接返回回答
    if not assistant_message.tool_calls:
        if verbose:
            print("💬 LLM 直接回答（未调用工具）")
        return assistant_message.content

    # 步骤 4：执行工具调用
    if verbose:
        print(f"🔧 LLM 决定调用 {len(assistant_message.tool_calls)} 个工具")

    messages.append(assistant_message.model_dump())

    for tool_call in assistant_message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        if verbose:
            print(f"  → {func_name}({func_args})")

        # 执行工具
        if func_name in tool_registry:
            result = tool_registry[func_name](**func_args)
        else:
            result = json.dumps({"error": f"未知工具：{func_name}"})

        if verbose:
            print(f"  ← {result[:200]}")  # 截断过长的输出

        # 步骤 5：将结果追加到消息历史
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

    # 步骤 6：再次调用 LLM 生成最终回答
    final_response = client.chat.completions.create(
        model=model, messages=messages,
        tools=tools, temperature=0.7, max_tokens=2048
    )

    final_answer = final_response.choices[0].message.content
    if verbose:
        print(f"✅ 最终回答生成完成")

    return final_answer


# 定义工具的 JSON Schema —— 这是 LLM 的"工具说明书"
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "获取指定城市的当前天气信息，包括气温（摄氏度）、天气状况和湿度。"
                "当用户询问某个城市的天气、气温、是否需要带伞/穿外套等问题时，调用此工具。"
                "目前支持的城市：北京、上海、广州、深圳、杭州。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要查询天气的城市名称，例如：北京、上海、广州，对应的日期，例如：今天、明天、后天，以及需要查询的天气信息，例如：天气、气温、湿度等"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "执行数学计算，支持加减乘除、幂运算、三角函数、对数等。"
                "当用户需要精确计算数学表达式时调用此工具。"
                "输入应为合法的 Python 数学表达式，例如：'2**10'、'sqrt(144)'、'7654321 * 1234567'。"
                "注意：不要用此工具回答不涉及计算的问题。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，使用 Python 语法，例如：'2**10'、'sqrt(144)'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def get_weather(query: str) -> str:
    """
    使用 Tavily 搜索天气信息的底层真实函数
    """
    print(f"\n🌍 [Tool 执行中] 正在通过 Tavily 搜索: {query} ...")

    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": "key",
        "query": query,
        "search_depth": "basic",  # 基础搜索速度更快
        "include_answer": True,  # 让 Tavily 尝试直接提取简短回答
        "max_results": 3  # 只要前 3 个最相关的网页结果
    }
    return json.dumps({"status": "success"}, ensure_ascii=False)


def calculate(expression: str) -> str:
    """安全的数学计算工具，支持基本运算和常用数学函数"""
    # 安全白名单：只允许数学相关的函数和运算符
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "pow": pow, "sum": sum,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
    }

    try:
        # 使用 eval 配合白名单，防止代码注入
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return json.dumps({
            "expression": expression,
            "result": result,
            "status": "success"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "expression": expression,
            "error": str(e),
            "status": "failed"
        }, ensure_ascii=False)


# 建立工具名称到函数的映射（工具注册表），方便根据 LLM 返回的名称动态调用
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculate": calculate,
}

# 测试 1：需要天气工具的问题
print("=" * 60)
print("测试 1：天气查询")
print("=" * 60)

answer = function_calling_pipeline(
    "上海今天天气怎么样？需要带伞吗？",
    tools=tools,
    tool_registry=TOOL_REGISTRY
)
print(f"\n🤖 {answer}\n")

# 测试 2：需要计算工具的问题
print("=" * 60)
print("测试 2：数学计算")
print("=" * 60)
answer = function_calling_pipeline(
    "请帮我计算 2 的 20 次方是多少？",
    tools=tools,
    tool_registry=TOOL_REGISTRY
)
print(f"\n🤖 {answer}\n")

# 测试 3：不需要工具的问题
print("=" * 60)
print("测试 3：纯知识问答（不需要工具）")
print("=" * 60)
answer = function_calling_pipeline(
    "请简要解释什么是 Function Calling？",
    tools=tools,
    tool_registry=TOOL_REGISTRY
)
print(f"\n🤖 {answer}\n")

# 测试 4：需要同时调用两个工具的问题
print("=" * 60)
print("测试 4：多工具调用")
print("=" * 60)
answer = function_calling_pipeline(
    "北京今天多少度？另外帮我算一下 sqrt(144) + 3.14 * 2",
    tools=tools,
    tool_registry=TOOL_REGISTRY
)
print(f"\n🤖 {answer}")
