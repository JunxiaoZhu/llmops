#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/1 14:42
@Author  : thezehui@gmail.com
@File    : app_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField
# 所有的校验规则，都在这里
from wtforms.validators import DataRequired, Length


# Completion 是被校验的方法名，与其保持一致；
# Req 是后缀；
class CompletionReq(FlaskForm):
    """基础聊天接口请求验证"""
    # 必填、长度最大为2000
    # req 是传入的参数名
    # 注意：这里等于号两边的req，都要与参数名保持一致
    req = StringField("req", validators=[
        DataRequired(message="用户的提问是必填"),
        Length(max=2000, message="用户的提问最大长度是2000"),
    ])
