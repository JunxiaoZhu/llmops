"""
@Time    : 2026/11/6
@Author  : zhujunxiao
@File    : PromptTemplate提示词模板
"""
from langchain_core.prompts import ChatPromptTemplate

# 使用messages模板字符串（最常用）
chat_template = ChatPromptTemplate.from_messages([
    # SystemMessage: 定义AI角色和行为准则
    ("system", "你是一个专业的Python代码审查助手。请严格检查代码风格、潜在Bug和性能问题。"),
    # HumanMessage: 用户输入
    ("human", "请审查以下代码：\n\n{code_snippet}"),
    # AIMessage: 可选，提供示例输出（Few-shot）
    ("ai", "我发现了以下问题：1. 缺少类型注解 2. 使用全局变量"),
    # HumanMessage: 用户的后续指令
    ("human", "{follow_up_instruction}")
])

# 格式化：生成消息列表
messages = chat_template.format_messages(
    code_snippet="def add(a,b):\n    return a+b",
    follow_up_instruction="请给出优化后的代码"
)

print("生成的消息结构：")
# enumerate 是 Python 的内置函数，用于在遍历可迭代对象时同时获取索引和元素值。
for i, msg in enumerate(messages):
    print(f"\n--- 消息 {i + 1} ---")
    print(f"内容: {msg.content}")
