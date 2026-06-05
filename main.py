#!/usr/bin/env python3
"""
天气助手 - Agent 主入口

实现一个简单的对话系统，能够识别天气相关问题并调用天气查询技能

核心组件：
1. 意图识别器：判断用户输入是否为天气问题
2. 技能调用器：调用 AmapWeatherSkill 获取天气信息
3. 对话管理器：处理用户交互流程
"""

from weather_skill import AmapWeatherSkill


def is_weather_question(user_input):
    """
    意图识别函数：判断用户输入是否为天气相关问题
    
    简化版意图识别：通过关键词匹
    user_input (str): 用户输入的问题
    
    返回:
    bool: 如果是天气问题返回 True，否则返回 False
    """
    # 天气相关关键词列表
    weather_keywords = [
        "天气", "气温", "温度", "多少度", "热不热", "冷不冷",
        "晴", "阴", "雨", "雪", "风", "霾", "雾",
        "预报", "查询", "看看", "查一下", "今天", "明天"
    ]
    
    # 转换为小写进行比较（不区分大小写）
    input_lower = user_input.lower()
    
    # 检查是否包含任何天气关键词
    for keyword in weather_keywords:
        if keyword in input_lower:
            return True
    
    return False


def extract_city(user_input):
    """
    从用户输入中提取城市名（简化版）
    
    假设用户输入格式为："城市名 + 天气相关词"
    
    参数:
    user_input (str): 用户输入的问题
    
    返回:
    str: 提取出的城市名，如果无法提取返回 None
    """
    # 常见城市列表（可扩展）
    common_cities = [
        "北京", "上海", "广州", "深圳", "杭州", "成都",
        "南京", "武汉", "西安", "重庆", "天津", "苏州",
        "郑州", "长沙", "沈阳", "青岛", "济南", "哈尔滨",
        "福州", "厦门", "南宁", "昆明", "贵阳", "兰州"
    ]
    
    # 在输入中查找城市名
    for city in common_cities:
        if city in user_input:
            return city
    
    return None


def extract_day(user_input):
    """
    从用户输入中提取时间信息
    
    参数:
    user_input (str): 用户输入的问题
    
    返回:
    int: 天数，0=今天，1=明天，2=后天，3=大后天，默认0
    """
    # 时间关键词映射（长关键词放在前面，避免子字符串匹配问题）
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
    
    # 在输入中查找时间关键词
    for keyword, day in day_keywords:
        if keyword in user_input:
            return day
    
    return 0


def get_day_description(day):
    """
    获取天数的中文描述
    
    参数:
    day (int): 天数
    
    返回:
    str: 中文描述
    """
    day_descriptions = ["今天", "明天", "后天", "大后天"]
    if 0 <= day < len(day_descriptions):
        return day_descriptions[day]
    return f"{day}天后"


def format_weather_response(weather_data, day=0):
    """
    格式化天气数据为友好的回复文本
    
    参数:
    weather_data (dict): 天气信息字典
    day (int): 天数，用于区分实时天气和预报
    
    返回:
    str: 格式化后的回复文本
    """
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


def main():
    """
    主函数：天气助手对话入口
    
    实现流程：
    1. 初始化天气技能
    2. 进入对话循环
    3. 获取用户输入
    4. 意图识别
    5. 如果是天气问题，提取城市并调用技能
    6. 返回结果给用户
    """
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
        # 获取用户输入
        user_input = input("\n你好！你想了解什么？\n> ").strip()
        
        # 退出条件
        if user_input.lower() in ["退出", "q", "quit", "exit"]:
            print("👋 再见！")
            break
        
        # 意图识别
        if is_weather_question(user_input):
            # 提取城市名和时间
            city = extract_city(user_input)
            day = extract_day(user_input)
            day_text = get_day_description(day)
            
            if city:
                print(f"🔍 正在查询 {city} {day_text} 的天气...")
                
                # 调用天气技能
                weather_data = weather_skill.get_weather(city, day)
                
                if weather_data:
                    # 格式化并输出结果
                    response = format_weather_response(weather_data, day)
                    print("\n" + "=" * 30)
                    print(response)
                    print("=" * 30)
                else:
                    print(f"😔 抱歉，未能获取到 {city} {day_text} 的天气信息")
            else:
                print("🤔 我没听清楚你想查询哪个城市，请重新输入")
        
        else:
            # 非天气问题的回复
            print("😅 我只会查天气哦，请问你想查什么？")


if __name__ == "__main__":
    main()
