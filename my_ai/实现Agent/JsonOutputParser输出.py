"""
@Time    : 2026/11/7
@Author  : zhujunxiao
@File    : JsonOutputParser输出
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv(override=True)


# 1. 定义输出结构
class WeatherInfo(BaseModel):
    """天气信息"""
    city: str = Field(description="城市名称")
    temperature: int = Field(description="温度（摄氏度）")
    condition: str = Field(description="天气状况")


# 2. 创建 JSON 输出解析器
json_parser = JsonOutputParser(pydantic_object=WeatherInfo)

# 3. 创建提示模板（关键：必须包含 "json" 这个词）
prompt = ChatPromptTemplate.from_template(

    """请根据以下信息提取天气数据，并以 JSON 格式返回。
    
    信息：{weather_info}
    
    请返回包含以下字段的 JSON：
    - city: 城市名称
    - temperature: 温度（摄氏度）
    - condition: 天气状况
    
    必须返回以下 JSON 格式（不要包含任何其他文本）：
    {{"city": "城市名称", "temperature": 温度数字, "condition": "天气状况"}}
    
    例如：{{"city": "北京", "temperature": 25, "condition": "晴"}}
    
    JSON 格式：
    """)

# 4. 定义模型
model = init_chat_model(  # 通用工厂方法，可以按 model_provider 创建不同聊天模型（不同的厂商）
    model="deepseek-chat",
    model_provider="deepseek",  # 指定模型供应商
)

# 5. 构建链
runnable = prompt | model | json_parser

# 6. 调用
result = runnable.invoke({"weather_info": "北京今天晴，温度25度"})
print(result)
print(result["city"])
