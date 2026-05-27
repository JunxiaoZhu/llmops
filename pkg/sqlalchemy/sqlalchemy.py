#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/6 21:08
@Author  : thezehui@gmail.com
@File    : sqlalchemy.py
"""
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQAlchemy


# 这里是“实例绑定注入”，不是“类构造注入”，因此 SQLAlchemy 类本身不用 @inject
# 通过 app.http.module.ExtensionModule 实现“实例绑定”
class SQLAlchemy(_SQAlchemy):
    """重写Flask-SQLAlchemy中的核心类，实现自动提交"""

    # @contextmanager、yield、with 配合使用；
    # with下面的操作，相当于在try之下，yield之前执行
    @contextmanager
    def auto_commit(self):
        try:
            # .... 执行位置
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()  # 回滚
            raise e  # 重新抛出，让上层调用者也能处理
