#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/29 15:10
@Author  : thezehui@gmail.com
@File    : http.py
"""
import os

from flask import Flask
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

from config import Config
from internal.exception import CustomException
from internal.router import Router
from pkg.response import json, Response, HttpCode
from pkg.sqlalchemy import SQLAlchemy


class Http(Flask):
    """Http服务引擎"""

    # *args、 ** kwargs 构造函数中，常见的两中参数，
    # 前者表示一组值"，后者表示一组"字段名=值"
    def __init__(
            self,
            *args,  # 无命名参数
            conf: Config,
            db: SQLAlchemy,
            migrate: Migrate,
            router: Router,
            **kwargs,  # 有命名参数
    ):
        # 1.调用父类构造函数初始化
        super().__init__(*args, **kwargs)

        # 2.初始化应用配置
        self.config.from_object(conf)

        # 3.注册绑定异常错误处理
        self.register_error_handler(Exception, self._register_error_handler)

        # 4.初始化flask扩展
        db.init_app(self)

        # with 上下文管理关键字，打开app上下文
        # 创建表（没有则创建）
        # 使用 db.create_all() 同步表结构，会有一个问题，
        # 如果model中新增了一个字段，得先调用 db.drop_all() 删除所有表，在建才能同步，这样肯定不行！
        # with self.app_context():
        #    db.create_all()

        # 使用以下方法，则不会有这个问题
        # internal/migration 是会自动创建的文件夹
        # flask --app app.http.app db init 初始化文件夹，其中app.http.app是指启动模块的位置
        # flask --app app.http.app db migrate 生成版本，会在数据库生成alembic_version表，记录版本号
        # flask --app app.http.app db upgrade 同步表结构
        migrate.init_app(self, db, directory="internal/migration")

        # 5.注册应用路由
        router.register_router(self)

    def _register_error_handler(self, error: Exception):
        # 1.异常信息是不是我们的自定义异常，如果是可以提取message和code等信息
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data is not None else {},
            ))
        # 2.HTTP框架级异常(如404/405)保留原始状态码，不再被包装为500
        if isinstance(error, HTTPException):
            return error
        # 3.如果不是我们的自定义异常，则有可能是程序、数据库抛出的异常，也可以提取信息，设置为FAIL状态码
        if self.debug or os.getenv("FLASK_ENV") == "development":
            raise error
        else:
            return json(Response(
                code=HttpCode.FAIL,
                message=str(error),
                data={},
            ))
