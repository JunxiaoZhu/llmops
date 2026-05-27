"""
@Time    : 2026/5/21
@Author  : zhujunxiao
@File    : test.py
"""
from typing import Any


class Chain:
    mylist: list

    def __init__(self, mylist: list):
        self.mylist = mylist

    def digui(self, input: Any):
        for li in self.mylist:
            input = li.invoke(input)
