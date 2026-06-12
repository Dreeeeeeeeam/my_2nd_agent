"""
天气技能类 - AmapWeatherSkill

封装高德地图天气查询功能，提供统一的接口供Agent调用
"""

import requests
from config import (
    AMAP_API_KEY,
    REQUEST_TIMEOUT,
    AMAP_GEOCODE_URL,
    AMAP_WEATHER_URL
)


class AmapWeatherSkill:
    """
    高德地图天气查询技能类
    
    提供根据城市名获取实时天气的能力
    """
    
    def __init__(self):
        """
        初始化技能类
        """
        # 验证API Key
        if not AMAP_API_KEY or AMAP_API_KEY == "your_api_key_here":
            raise ValueError("请先在 config.py 中配置你的高德地图API Key")
        
        self.api_key = AMAP_API_KEY
    
    def _get_adcode(self, city):
        """
        内部方法：调用地理编码API获取城市的adcode
        
        参数:
         city (str): 城市名称
        返回:
        str: adcode（行政区划代码），失败返回None
        """
        params = {
            "address": city,
            "key": self.api_key
        }
        
        try:
            response = requests.get(
                AMAP_GEOCODE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") != "1":
                return None
            
            geocodes = data.get("geocodes", [])
            if not geocodes:
                return None
            
            return geocodes[0].get("adcode")
            
        except Exception:
            return None
    
    def get_weather(self, city, day=0):
        """
        根据城市名获取天气信息
        
        参数:
        city (str): 城市名称（中文，如 "北京"、"上海"）
        day (int): 天数，0=今天（实时），1=明天，2=后天，最多支持3天
        
        返回:
        dict: 天气信息字典，格式如下：
              {
                  "city": "城市名",
                  "temperature": 温度(°C),
                  "weather": "天气状况",
                  "wind_direction": "风向",
                  "wind_power": "风力",
                  "humidity": "湿度(%)",
                  "report_time": "更新时间"
              }
              查询失败返回 None
        """
        # 验证输入
        if not city or not isinstance(city, str):
            return None
        
        # 验证day参数
        if not isinstance(day, int) or day < 0 or day > 3:
            day = 0
        
        # 第一步：获取adcode
        adcode = self._get_adcode(city)
        if not adcode:
            return None
        
        # 第二步：获取天气
        # day=0时使用base获取实时天气，day>0时使用all获取预报
        params = {
            "city": adcode,
            "key": self.api_key,
            "extensions": "all" if day > 0 else "base"
        }
        
        try:
            response = requests.get(
                AMAP_WEATHER_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") != "1":
                return None
            
            # 获取实时天气或预报
            if day == 0:
                # 获取实时天气
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
            else:
                # 获取未来天气预报
                forecasts = data.get("forecasts", [])
                if not forecasts:
                    return None
                
                forecast = forecasts[0]
                casts = forecast.get("casts", [])
                
                # 检查是否有足够的预报数据
                if day >= len(casts):
                    return None
                
                cast = casts[day]
                
                return {
                    "city": forecast.get("city", city),
                    "temperature": float(cast.get("daytemp_float", cast.get("daytemp", 0))),
                    "weather": cast.get("dayweather", "未知"),
                    "wind_direction": cast.get("daywind", "未知"),
                    "wind_power": cast.get("daypower", "未知"),
                    "humidity": 0,  # 预报不包含湿度数据
                    "report_time": cast.get("date", "未知")
                }
            
        except Exception:
            return None
