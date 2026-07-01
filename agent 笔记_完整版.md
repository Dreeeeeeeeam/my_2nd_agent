# Agent学习笔记

## 一、天气技能类分析

### 1.1 类的构成
class AmapWeatherSkill:
类的构成：一共由三个函数组成：
- `__init__(self)`: 初始化函数
- `_get_adcode(self, city)`: 主方法的内部方法，用来获取城市的adcode（城市代码）
- `get_weather(self, city, day=0)`: 主方法，根据输入的参数获取天气信息

### 1.2 函数介绍

#### 初始化函数：
```python
def __init__(self):
    if not AMAP_API_KEY or AMAP_API_KEY == "your_api_key_here":
        raise ValueError("请先在 config.py 中配置你的高德地图API Key")
    self.api_key = AMAP_API_KEY
```
- 用`self.api_key = AMAP_API_KEY`引入高德地图的api key
- 验证API Key的有效性，确保配置正确

#### 内部方法 `_get_adcode`
2.2.1 接收city参数
2.2.2 声明请求
```python
response = requests.get(
    AMAP_GEOCODE_URL,
    params=params,
    timeout=REQUEST_TIMEOUT
)
response.raise_for_status()
```
**注**：response是requests.get的输出结果对象，是一个数据包，通常包括：
- 状态码status code
- 响应内容text / content / json
- 响应头headers

`response.raise_for_status()`这个方法用来检测数据包的状态码：
- 如果状态码表示成功（200-299）：方法什么都不做，程序继续向下执行
- 如果状态码表示错误（400-599）：它会立即抛出一个`requests.exceptions.HTTPError`异常
- 简单来说，它是确保“只有拿到成功的响应包，才去拆包看内容”的一道安全防线

2.2.3 提取城市代码：
```python
data = response.json()  # 将json转换成字典
if data.get("status") != "1":  # “1”指的是请求处理成功
    return None
geocodes = data.get("geocodes", [])
if not geocodes:
    return None
return geocodes[0].get("adcode")
```

#### 主方法 `get_weather`
接收两个参数 `city` 和 `day`（默认为0）

**第一步**：获取adcode（通过内部方法）
```python
adcode = self._get_adcode(city)
```

**第二步**：获取天气
```python
lives = data.get("lives", [])
if not lives:
    return None
live = lives[0]
return {
    "city": live.get("city", city),
    "temperature": float(live.get("temperature", 0)),
    "weather": live.get("weather", "未知"),
    "wind_direction": live.get("winddirection", "未知"),
    "wind_power": live.get("windpower", "未知"),
    "humidity": int(live.get("humidity", 0)),
    "report_time": live.get("reporttime", "未知")
}
```

**注**：通过day参数判断查询的是今天，明天还是后天的天气。返回的格式是字典，具体如下：
```python
{
    "city": "城市名",
    "temperature": 温度(°C),
    "weather": "天气状况",
    "wind_direction": "风向",
    "wind_power": "风力",
    "humidity": "湿度(%)",
    "report_time": "更新时间"
}
```

将该类封装，模块化编程。

---

## 二、主入口代码分析

### 2.1 代码组成
- `is_weather_question(user_input)`: 意图识别函数
- `extract_city(user_input)`: 提取城市名函数
- `extract_day(user_input)`: 提取时间函数
- `get_day_description(day)`: 获取天数的中文描述函数
- `format_weather_response(weather_data, day=0)`: 格式化天气数据函数
- `main()`: 主函数

### 2.2 函数介绍

#### 意图识别函数
```python
def is_weather_question(user_input):
    weather_keywords = [
        "天气", "气温", "温度", "多少度", "热不热", "冷不冷",
        "晴", "阴", "雨", "雪", "风", "霾", "雾",
        "预报", "查询", "看看", "查一下", "今天", "明天"
    ]
    input_lower = user_input.lower()
    for keyword in weather_keywords:
        if keyword in input_lower:
            return True
    return False
```
遍历天气关键词列表，检查用户输入是否包含天气关键词，有就返回True，无则返回False。

#### 提取城市名函数
```python
def extract_city(user_input):
    common_cities = [
        "北京", "上海", "广州", "深圳", "杭州", "成都",
        "南京", "武汉", "西安", "重庆", "天津", "苏州",
        "郑州", "长沙", "沈阳", "青岛", "济南", "哈尔滨",
        "福州", "厦门", "南宁", "昆明", "贵阳", "兰州"
    ]
    for city in common_cities:
        if city in user_input:
            return city
    return None
```
遍历城市名列表，检查用户输入是否含有城市名，如果有就返回城市名，无则返回None。

#### 提取时间函数
```python
def extract_day(user_input):
    day_keywords = [
        ("大后天", 3),
        ("今天", 0),
        ("现在", 0),
        ("当前", 0),
        ("此刻", 0),
        ("明天", 1),
        ("明日", 1),
        ("后天", 2),
    ]
    for keyword, day in day_keywords:
        if keyword in user_input:
            return day
    return 0
```
遍历（keyword, day），如果用户输入包含关键词，返回对应的day，若无则默认返回0，表示实时天气。

#### 获取天数的中文描述函数
```python
def get_day_description(day):
    day_descriptions = ["今天", "明天", "后天", "大后天"]
    if 0 <= day < len(day_descriptions):
        return day_descriptions[day]
    return f"{day}天后"
```
接收提取时间函数的返回值，根据索引返回对应的中文描述

#### 格式化天气数据函数
```python
def format_weather_response(weather_data, day=0):
    if not weather_data:
        return "抱歉，未能获取到天气信息"
    
    day_text = get_day_description(day)
    
    response = f"📍 {weather_data['city']} {day_text}天气\n"
    response += f"🌡️ 温度: {weather_data['temperature']}°C\n"
    response += f"☁️ 天气: {weather_data['weather']}\n"
    response += f"💨 风向: {weather_data['wind_direction']}风\n"
    response += f"🌬️ 风力: {weather_data['wind_power']}级\n"
    
    # 只有实时天气有湿度数据
    if day == 0 and weather_data.get('humidity', 0) > 0:
        response += f"💧 湿度: {weather_data['humidity']}%\n"
    
    if day == 0:
        response += f"⏰ 更新时间: {weather_data['report_time']}"
    else:
        response += f"📅 日期: {weather_data['report_time']}"
    
    return response
```
- 将天气数据格式化为友好的回复文本
- 使用emoji增强视觉效果
- 根据day参数区分实时天气和预报数据的显示内容

#### 主函数 `main()`
```python
def main():
    print("🌤️ 天气助手启动中...")
    
    try:
        # 初始化天气技能
        weather_skill = AmapWeatherSkill()
        print("✅ 天气技能加载成功")
    except ValueError as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    print("\n欢迎使用天气助手！")
    print("我可以帮你查询国内城市的天气，支持今天、明天、后天、大后天")
    print("输入 '退出' 或 'q' 可以结束对话")
    print("=" * 40)
    
    # 对话循环
    while True:
        user_input = input("\n你好！你想了解什么？\n> ").strip()
        
        if user_input.lower() in ["退出", "q", "quit", "exit"]:
            print("👋 再见！")
            break
        
        if is_weather_question(user_input):
            city = extract_city(user_input)
            day = extract_day(user_input)
            day_text = get_day_description(day)
            
            if city:
                print(f"🔍 正在查询 {city} {day_text} 的天气...")
                weather_data = weather_skill.get_weather(city, day)
                
                if weather_data:
                    response = format_weather_response(weather_data, day)
                    print("\n" + "=" * 30)
                    print(response)
                    print("=" * 30)
                else:
                    print(f"😔 抱歉，未能获取到 {city} {day_text} 的天气信息")
            else:
                print("🤔 我没听清楚你想查询哪个城市，请重新输入")
        else:
            print("😅 我只会查天气哦，请问你想查什么？")
```
- 实现完整的对话流程
- 处理用户输入和系统输出
- 协调各个函数完成天气查询任务

---

## 三、代码优化建议

### 3.1 意图识别优化
当前实现：简单关键词匹配
```python
def is_weather_question(user_input):
    weather_keywords = ["天气", "气温", ...]
    return any(keyword in user_input.lower() for keyword in weather_keywords)
```

优化方案：使用正则表达式精确匹配
```python
import re

def is_weather_question(user_input):
    patterns = [
        r'.*(今天|明天|后天|大后天).*(天气|气温|温度)',
        r'.*(天气|气温|温度).*(今天|明天|后天|大后天)',
        r'([\u4e00-\u9fa5]+)(的)?(天气|气温|温度)'
    ]
    return any(re.search(pattern, user_input) for pattern in patterns)
```

### 3.2 城市识别优化
当前实现：仅支持常见城市列表
```python
def extract_city(user_input):
    common_cities = ["北京", "上海", ...]
    return next((city for city in common_cities if city in user_input), None)
```

优化方案：调用地理编码API实时查询
```python
def extract_city(user_input):
    # 使用模糊匹配和API查询结合
    # 先尝试本地匹配，再调用API
    pass
```

### 3.3 错误处理增强
当前实现：简单异常捕获
```python
try:
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
except Exception:
    return None
```

优化方案：添加详细日志
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP请求错误: {e}")
    return None
except requests.exceptions.ConnectionError as e:
    logger.error(f"网络连接错误: {e}")
    return None
except requests.exceptions.Timeout as e:
    logger.error(f"请求超时: {e}")
    return None
except Exception as e:
    logger.error(f"未知错误: {e}")
    return None
```

---

## 四、学习总结

### 4.1 核心知识点
1. **模块化设计**：将天气查询功能封装为独立的类，提高代码复用性
2. **API调用**：掌握第三方API的调用方法和数据解析
3. **错误处理**：学会处理网络请求中的各种异常情况
4. **用户体验**：设计友好的交互流程和输出格式

### 4.2 技术要点
- Python类的定义和使用
- requests库的基本用法
- JSON数据解析
- 正则表达式应用
- 日志记录

### 4.3 扩展方向
1. **多轮对话**：支持上下文关联，如用户问"北京明天天气"后，再问"后天呢"能自动关联北京
2. **语音交互**：集成语音识别和合成功能
3. **多源数据**：支持调用多个天气API提高可靠性
4. **前端界面**：开发Web或GUI界面
5. **智能推荐**：根据天气情况提供出行建议