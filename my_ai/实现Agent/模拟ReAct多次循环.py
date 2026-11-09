"""
@Time    : 2026/11/5
@Author  : zhujunxiao
@File    : 模拟ReAct多次循环
"""
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"  # DeepSeek API 端点
)


# ==========================================
# 1. 准备你的工具（为了演示多次调用，准备两个工具）
# ==========================================
def search_web(query):
    print(f"👉 [执行工具 1] 正在全网搜索：{query}...")
    if "苹果" in query and "CEO" in query:
        return '{"result": "苹果现任CEO是蒂姆·库克（Tim Cook），他的净资产约为 20 亿美元。"}'
    elif "汇率" in query:
        return '{"result": "今天1美元兑换约149日元。"}'
    return '{"result": "没有找到相关信息。"}'


def multiply_numbers(a, b):
    print(f"👉 [执行工具 2] 正在利用计算器计算：{a} * {b}...")
    return json.dumps({"result": float(a) * float(b)})


available_functions = {
    "search_web": search_web,
    "multiply_numbers": multiply_numbers
}

tools_description = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索引擎。当需要查找人物信息、实时数据、汇率等知识时使用。",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "搜索关键词"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "计算器。当需要计算两个数字的乘积时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "第一个数字"},
                    "b": {"type": "number", "description": "第二个数字"}
                },
                "required": ["a", "b"]
            }
        }
    }
]


# ==========================================
# 2. 核心大循环引擎 (ReAct Runtime)
# ==========================================
def run_agent_loop(user_query, max_iterations=10):
    messages = [
        {"role": "system", "content": "你是一个能够自主拆解任务并使用工具的高级 AI 助手。"},
        {"role": "user", "content": user_query}
    ]

    print("====== 🎬 Agent 开始运行 ======")

    # 开始无尽的循环，直到任务完成或者超出最大轮数
    # range(1, 11) 生成一个从 1 开始、到 11 之前结束（即不包含 11）的整数序列：1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    for iteration in range(1, max_iterations + 1):
        print(f"\n🌀 第 {iteration} 轮思考开始...")

        # 1. 把目前的全部对话历史扔给大模型
        response = client.chat.completions.create(
            model="deepseek-chat",  # 在多次逻辑推理中表现更好
            messages=messages,
            tools=tools_description
        )

        assistant_message = response.choices[0].message

        # ⚠️ 不要忘记：先把大模型的此刻状态存入剧本
        messages.append(assistant_message)

        # 2. 终止条件判定：如果大模型觉得没必要调工具了（直接给出了自然语言回答），退出循环
        if not assistant_message.tool_calls:
            print("\n✅ Agent 决定结束任务，认为已经拿到最终答案。")
            return assistant_message.content

        # 3. 工具执行处理阶段：大模型要求调用工具
        for tool_call in assistant_message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            # --- 本地执行 ---
            if func_name in available_functions:
                result = available_functions[func_name](**func_args)
            else:
                result = f"Error: 找不到工具 {func_name}"

            # --- 拼装结果，准备进入下一轮 (严格对应 tool_call_id) ---
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": str(result)
            })

    # 如果把 range(1, 10) 全跑完了还没退出，说明陷入了死循环
    return "\n❌ 超过最大迭代次数，Agent 可能陷入死循环，被迫终止。"


# ==========================================
# 3. 开始测试刁钻问题
# ==========================================
if __name__ == "__main__":
    # 注意这里虽然不能联网搜索，但是训练数据中已经包含了苹果这种高频知识
    hard_question = "苹果公司的CEO是谁？他的净资产是多少？请把他的净资产（按美元算）乘以今天的日元汇率，告诉我大概等于多少日元。"
    # hard_question = "库克持有苹果股票吗？"
    print(f"👤 用户：{hard_question}\n")
    final_answer = run_agent_loop(hard_question)

    print("\n🎉 最终的大模型回复：")
    print("-" * 50)
    print(final_answer)
