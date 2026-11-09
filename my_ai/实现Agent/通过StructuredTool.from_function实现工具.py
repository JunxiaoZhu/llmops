"""
@Time    : 2026/11/8
@Author  : zhujunxiao
@File    : 通过StructuredTool.from_function实现工具
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

"""
1. 通过 Pydantic BaseModel 定义参数，提供：
- 参数描述（description）
- 必填/可选约束
- 更清晰的 Schema 文档
"""


class DivideInput(BaseModel):
    """除法工具输入参数"""
    dividend: float = Field(description="被除数")
    divisor: float = Field(description="除数，不能为零")


def divide(dividend: float, divisor: float) -> float:
    """执行除法运算，支持浮点数"""
    if divisor == 0:
        raise ValueError("除数不能为零")
    return dividend / divisor


# 2. 创建带参数校验的工具
division_tool = StructuredTool.from_function(
    func=divide,
    name="DivisionTool",
    description="安全执行除法运算，自动处理除零错误",
    args_schema=DivideInput,  # 显式指定参数模式
    return_direct=False,  # 是否直接返回工具结果（不经过 LLM 再次处理）
)

# 3. 测试参数校验（触发 Pydantic 验证）
try:
    division_tool.invoke({"a": 10, "b": 2})  # 错误：参数名不匹配
except Exception as e:
    print(f"参数校验失败：{e}")

# 4. 正确调用
result = division_tool.invoke({"dividend": 10, "divisor": 2})
print(f"除法结果：{result}")
