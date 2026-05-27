#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/9 18:49
@Author  : thezehui@gmail.com
@File    : 1.LLM与ChatModel使用技巧.py
"""
from datetime import datetime

import dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 需要使用秘钥
dotenv.load_dotenv()

# 1.编排prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是OpenAI开发的聊天机器人，请回答用户的问题，现在的时间是{now}"),
    ("human", "{query}"),
]).partial(now=datetime.now())

# 2.创建大语言模型
llm = ChatOpenAI(
    model="gpt-5.4",
    use_responses_api=True,
    # output_version="responses/v1",  # 这个可以理解成 格式协议名，用哪种“响应格式版本”去组织返回值
)

chunks = llm.stream(prompt.invoke({"query": "现在是几点，请讲一个程序员的冷笑话"}))

# 这是合成一行的写法
# content = "".join(chunk.text for chunk in chunks if getattr(chunk, "text", ""))

# 这是展开的写法
# llm.stream 流式输出，返回的是可迭代对象，所以取完值后，再想取值，就取不到了
parts = []
for chunk in chunks:  # 遍历取值
    # getattr 动态获取对象的属性 或 方法,属性名、方法名可通过传参设置
    text = getattr(chunk, "text", "")  # 这里的意思是取 chunk 对象中的 text 属性，没有则默认为 ""
    if text:  # 类似 text != "" 、 len(text) > 0
        parts.append(text)
content2 = "".join(parts)  # 把所有片段按 空分隔符 拼接起来

print("=================")
print(content2)
