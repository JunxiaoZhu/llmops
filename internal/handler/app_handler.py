#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/29 14:59
@Author  : thezehui@gmail.com
@File    : app_handler.py
"""
import uuid
from dataclasses import dataclass
from uuid import UUID

from flask import request
from injector import inject
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from internal.schema.app_schema import CompletionReq
from internal.service import AppService
from pkg.response import success_json, validate_error_json, success_message


@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    def create_app(self):
        """调用服务创建新的APP记录"""
        app = self.app_service.create_app()
        #   f 表示这个字符串支持 {} 插值
        return success_message(f"应用已经成功创建，id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_json({
            "id": str(app.id),
            "account_id": str(app.account_id),
            "name": app.name,
            "icon": app.icon,
            "description": app.description,
            "status": app.status,
            "updated_at": app.updated_at.isoformat() if app.updated_at else None,
            "created_at": app.created_at.isoformat() if app.created_at else None,
        })

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        #   f 表示这个字符串支持 {} 插值
        return success_message(f"应用已经成功修改，修改的名字是:{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message("应用已经成功删除，id为:{app.id}")

    def debug(self, app_id: UUID):
        """聊天接口"""
        # 1.提取从接口中获取的输入，POST
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.构建组件
        prompt = ChatPromptTemplate.from_template("{query}")
        llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
        parser = StrOutputParser()

        # 3.构建链
        chain = prompt | llm | parser

        # 4.调用链得到结果
        content = chain.invoke({"query": req.query.data})

        return success_json({"content": content})

    # def ping(self):
    # raise FailException("数据未找到")

    def ping(self):
        """聊天窗口"""
        req = request.json.get("req")

        # 字段校验
        com = CompletionReq()
        if not com.validate():
            return com.errors

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是聊天机器人，请回答用户的问题"),
            ("user", req)
        ])

        llm = ChatOpenAI(
            model="gpt-5.4",
            use_responses_api=True,
            # output_version="responses/v1",  # 这个可以理解成 格式协议名，用哪种“响应格式版本”去组织返回值
        )

        chin = prompt | llm
        chunks = chin.stream({})
        # chunks = llm.stream(prompt.format_messages())

        content = "".join(chunk.text for chunk in chunks if getattr(chunk, "text", ""))

        print("========" + content)
        return success_json({"content": content})
