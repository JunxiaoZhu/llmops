# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/10 17:44
@Author  : thezehui@gmail.com
@File    : 2.RunnableParallel模拟检索.py
"""
from operator import itemgetter

import dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


def retrieval(query: str) -> str:
    """一个模拟的检索器函数"""
    print("正在检索:", query)
    return "我是慕小课"


# 1.编排prompt
prompt = ChatPromptTemplate.from_template("""请根据用户的问题回答，可以参考对应的上下文进行生成。

<context>
{context}
</context>

用户的提问是: {query}""")

# 2.构建大语言模型
llm = ChatOpenAI(model="gpt-5.4", use_responses_api=True)

# 3.输出解析器
parser = StrOutputParser()

# 4.构建链
# 这里本质上是去取 {"query": "你好，我是谁?"} 中的值

# RunnablePassthrough.assign(context=lambda x: retrieval(x["query"]) 这种本质上是在 {"query": "你好，我是谁?"} 中添加值
chain = {
            "context": lambda x: retrieval(x["query"]),
            "query": itemgetter("query"),
        } | prompt | llm | parser

# 5.调用链
# 这里还可以写为：chain.invoke("你好，我是谁?"),
# 写成这种方式时，上面只能对应{...}这种格式，且需调整现在的写法
content = chain.invoke({"query": "你好，我是谁?"})

print(content)
