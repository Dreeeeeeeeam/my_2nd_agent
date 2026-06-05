"""
高德地图天气查询模块

功能：根据城市名查询“实时”天气信息
封装为独立函数 get_amap_data(city)
"""

# 导入必要的库
import requests

# 导入配置文件中的API Key和常量
from config import (
    AMAP_API_KEY,
    REQUEST_TIMEOUT,
    AMAP_GEOCODE_URL,
    AMAP_WEATHER_URL
)


def get_amap_data(city):
    """
    根据城市名获取高德地图天气数据

    参数:
    city (str): 城市名称（中文，如 "北京"、"上海"）

    返回:
    dict: 包含城市信息和天气数据的字典，格式如下：
          {
              "city": "城市名",
              "adcode": "行政区划代码",
              "temperature": 实时温度(摄氏度),
              "weather": "天气状况",
              "wind_direction": "风向",
              "wind_power": "风力",
              "humidity": "湿度(%)",
              "report_time": "数据更新时间"
          }
          如果查询失败返回 None
    """

    # 1. 验证输入参数
    if not city or not isinstance(city, str):
        print("错误：城市名不能为空且必须是字符串")
        return None

    # 2. 验证API Key是否已配置
    if not AMAP_API_KEY or AMAP_API_KEY == "your_api_key_here":
        print("错误：请先在 config.py 中配置你的高德地图API Key")
        return None

    # 3. 第一步：调用地理编码API获取城市的adcode
    print(f"正在查询城市 '{city}' 的地理编码...")

    # 准备地理编码请求参数
    geocode_params = {
        "address": city,  # 要查询的城市名称
        "key": AMAP_API_KEY  # 高德地图API Key
    }

    try:
        # 发送GET请求到地理编码API
        geocode_response = requests.get(
            url=AMAP_GEOCODE_URL,  # API地址
            params=geocode_params,  # 请求参数
            timeout=REQUEST_TIMEOUT  # 超时时间
        )

        # 检查HTTP状态码，非200则抛出异常
        geocode_response.raise_for_status()

        # 将JSON响应转换为Python字典
        geocode_data = geocode_response.json()

        # 检查API返回状态
        if geocode_data.get("status") != "1":
            error_info = geocode_data.get("info", "未知错误")
            print(f"地理编码失败: {error_info}")
            return None

        # 提取地理编码结果
        geocodes = geocode_data.get("geocodes", [])
        if not geocodes:
            print(f"未找到城市 '{city}' 的地理信息")
            return None

        # 获取城市的adcode（行政区划代码）和格式化地址
        adcode = geocodes[0].get("adcode")
        formatted_address = geocodes[0].get("formatted_address")

        print(f"✓ 地理编码成功: {formatted_address} (adcode: {adcode})")

    except requests.exceptions.Timeout:
        print("错误：网络请求超时，请检查网络连接")
        return None
    except requests.exceptions.ConnectionError:
        print("错误：网络连接失败，请检查网络连接")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"错误：HTTP请求失败 ({e})")
        return None
    except Exception as e:
        print(f"地理编码过程中发生未知错误: {e}")
        return None

    # 4. 第二步：调用天气API获取实时天气
    print(f"正在获取 '{city}' 的实时天气...")

    # 准备天气请求参数
    weather_params = {
        "city": adcode,  # 使用第一步获取的adcode
        "key": AMAP_API_KEY,  # 高德地图API Key
        "extensions": "base"  # base: 实况天气, all: 预报天气
    }

    try:
        # 发送GET请求到天气API
        weather_response = requests.get(
            url=AMAP_WEATHER_URL,  # API地址
            params=weather_params,  # 请求参数
            timeout=REQUEST_TIMEOUT  # 超时时间
        )

        # 检查HTTP状态码
        weather_response.raise_for_status()

        # 将JSON响应转换为Python字典
        weather_data = weather_response.json()

        # 检查API返回状态
        if weather_data.get("status") != "1":
            error_info = weather_data.get("info", "未知错误")
            print(f"天气查询失败: {error_info}")
            return None

        # 提取天气数据
        lives = weather_data.get("lives", [])
        if not lives:
            print(f"未获取到 '{city}' 的天气数据")
            return None

        # 提取具体天气信息
        live_data = lives[0]

        # 构建返回结果字典
        result = {
            "city": formatted_address,  # 城市名称
            "adcode": adcode,  # 行政区划代码
            "temperature": float(live_data.get("temperature", 0)),  # 实时温度
            "weather": live_data.get("weather", "未知"),  # 天气状况
            "wind_direction": live_data.get("winddirection", "未知"),  # 风向
            "wind_power": live_data.get("windpower", "未知"),  # 风力
            "humidity": int(live_data.get("humidity", 0)),  # 湿度
            "report_time": live_data.get("reporttime", "未知")  # 更新时间
        }

        print("✓ 天气查询成功")
        return result

    except requests.exceptions.Timeout:
        print("错误：网络请求超时，请检查网络连接")
        return None
    except requests.exceptions.ConnectionError:
        print("错误：网络连接失败，请检查网络连接")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"错误：HTTP请求失败 ({e})")
        return None
    except ValueError:
        print("错误：温度或湿度数据格式异常")
        return None
    except Exception as e:
        print(f"天气查询过程中发生未知错误: {e}")
        return None


# 示例用法
if __name__ == "__main__":


    print("=" * 50)
    print("高德地图天气查询工具")



    city = input("该工具可以查询实时天气，你想查询哪里的天气？\n请输入你要查询的城市:")
    # 调用封装好的函数

    weather_result = get_amap_data(city)
    # 打印查询结果
    print(f"城市: {weather_result['city']}")
    print(f"温度: {weather_result['temperature']}°C")
    print(f"天气: {weather_result['weather']}")
    print(f"风向: {weather_result['wind_direction']}")
    print(f"风力: {weather_result['wind_power']}")
    print(f"湿度: {weather_result['humidity']}%")
    print(f"更新时间: {weather_result['report_time']}")

    print("查询结束")
    print("=" * 50)

    # # 测试城市列表
    # test_cities = ["北京", "上海", "广州", "深圳", "杭州"]
    #
    # for city in test_cities:
    #     print(f"\n查询城市: {city}")
    #     print("-" * 30)
    #
    #     # 调用封装好的函数
    #     weather_result = get_amap_data(city)
    #
    #     if weather_result:
    #         # 打印查询结果
    #         print(f"城市: {weather_result['city']}")
    #         print(f"温度: {weather_result['temperature']}°C")
    #         print(f"天气: {weather_result['weather']}")
    #         print(f"风向: {weather_result['wind_direction']}")
    #         print(f"风力: {weather_result['wind_power']}")
    #         print(f"湿度: {weather_result['humidity']}%")
    #         print(f"更新时间: {weather_result['report_time']}")
    #     else:
    #         print(f"✗ 查询失败")
    #
    # print("\n" + "=" * 50)
    # print("查询完成")
    # print("=" * 50)
