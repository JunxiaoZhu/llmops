"""由 MCP 客户端启动的本地数学服务器。"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("math")


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """计算 a 减 b，可用于计算两个温度的差值。"""
    return a - b


if __name__ == "__main__":
    # stdout 用于 MCP 协议通信，不要在这里打印普通日志。
    mcp.run(transport="stdio")
