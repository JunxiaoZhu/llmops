#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/5 19:03
@Author  : thezehui@gmail.com
@File    : module.py
"""
from flask_migrate import Migrate
from injector import Module, Binder

from internal.extension.database_extension import db
from internal.extension.migrate_extension import migrate
from pkg.sqlalchemy import SQLAlchemy


# 这里是“实例绑定注入”，不是“类构造注入”，因此 SQLAlchemy 类本身不用 @inject
# 通过 app.http.module.ExtensionModule 实现“实例绑定”
class ExtensionModule(Module):
    """扩展模块的依赖注入（第三方工具）"""

    # 单例模式，整个应用的生命周期，只创建一次
    def configure(self, binder: Binder) -> None:
        # 这里的db，就是实例对象
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
