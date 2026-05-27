#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/10 1:33
@Author  : thezehui@gmail.com
@File    : 2.JsonOutputParser使用技巧.py
"""
import dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

dotenv.load_dotenv()


# 1.创建一个json数据结构，用于告诉大语言模型这个json长什么样子
class Joke(BaseModel):  # BaseModel 会检查字段类型是否符合；可以将整个对象转JSON；
    # 冷笑话
    joke: str = Field(description="回答用户的冷笑话")
    # 冷笑话的笑点
    punchline: str = Field(description="这个冷笑话的笑点")


# 创建解析器，指定要解析成 Joke 对象
parser = JsonOutputParser(pydantic_object=Joke)

#
gfi = parser.get_format_instructions()

print("=======" + gfi)

print("==============")

# 2.构建一个提示模板
prompt = (ChatPromptTemplate.from_template("请根据用户的提问进行回答。\n{format_instructions}\n{query}")
          .partial(format_instructions=gfi))

# 3.构建一个大语言模型
llm = ChatOpenAI(
    model="gpt-5.4",
    use_responses_api=True,
    # output_version="responses/v1",  # 这个可以理解成 格式协议名，用哪种“响应格式版本”去组织返回值
)

# 4.传递提示并进行解析
joke = parser.invoke(llm.invoke(prompt.invoke({"query": "请讲一个关于程序员的冷笑话"})))

print(type(joke))
print(joke.get("punchline"))
print(joke)
