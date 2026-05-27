#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/10 1:24
@Author  : thezehui@gmail.com
@File    : 1.StrOutputParser使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

# 1.编排提示模板
prompt = ChatPromptTemplate.from_template("{query}")

# 2.构建大语言模型
llm = ChatOpenAI(
    model="gpt-5.4",
    use_responses_api=True,
    # output_version="responses/v1",  # 这个可以理解成 格式协议名，用哪种“响应格式版本”去组织返回值
)

# 3.创建字符串输出解析器
parser = StrOutputParser()

# 4.调用大语言模型生成结果并解析
chunks = llm.stream(prompt.invoke({"query": "你好，你是?"}))

# llm.stream 流式输出，返回的是可迭代对象，所以取完值后，再想取值，就取不到了
parts = []
for chunk in chunks:  # 遍历取值
    # getattr 动态获取对象的属性 或 方法,属性名、方法名可通过传参设置
    text = getattr(chunk, "text", "")  # 这里的意思是取 chunk 对象中的 text 属性，没有则默认为 ""
    if text:  # 类似 text != "" 、 len(text) > 0
        parts.append(text)
content = "".join(parts)  # 把所有片段按 空分隔符 拼接起来

# 转成字符串，内容不变
content2 = parser.invoke(content)

print(content)
print("=============")
print(content2)
