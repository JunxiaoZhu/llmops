"""
功能描述：
:author: zhujunxiao
:date: 2026/4/14 16:29
"""
from dataclasses import dataclass

from injector import Injector, inject


class A:
    name: str = "-------junxiao"


@inject
@dataclass  # 加上dataclass，可以删掉下面的构造函数
class B:
    a: A

    def print(self):
        print(self.a.name)


injector = Injector()
b = injector.get(B)
b.print()
