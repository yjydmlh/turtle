"""
时间维度枚举
用于和表名拼接成完整的视图名字，如 btc_usdt_5m, eth_usdt_1h 等
"""
from enum import Enum


class TimeframeEnum(Enum):
    """时间维度枚举"""
    
    M1 = "1m"      # 1分钟
    M5 = "5m"      # 5分钟
    M15 = "15m"    # 15分钟
    M30 = "30m"    # 30分钟
    H1 = "1h"      # 1小时
    H4 = "4h"      # 4小时
    D1 = "1d"      # 1天
    W1 = "1w"      # 1周
    MO1 = "1mo"    # 1个月
    
    def __new__(cls, suffix: str):
        """
        创建枚举项
        
        Args:
            suffix: 时间维度后缀（如 5m, 1h, 1d）
        """
        obj = object.__new__(cls)
        obj._value_ = suffix
        obj.suffix = suffix
        return obj
    
    def build_view_name(self, table_prefix: str) -> str:
        """
        构建完整的视图名称
        
        Args:
            table_prefix: 表名前缀（如 btc_usdt, eth_usdt）
        
        Returns:
            完整的视图名称（如 btc_usdt_5m, eth_usdt_1h）
        
        Example:
            timeframe = TimeframeEnum.M5
            view_name = timeframe.build_view_name("btc_usdt")  # 返回 "btc_usdt_5m"
        """
        return f"{table_prefix}_{self.suffix}"
    
    @classmethod
    def from_suffix(cls, suffix: str) -> "TimeframeEnum":
        """
        根据后缀获取枚举项
        
        Args:
            suffix: 时间维度后缀（如 5m, 1h, 1d）
        
        Returns:
            对应的枚举项
        
        Raises:
            ValueError: 如果找不到对应的枚举项
        """
        for item in cls:
            if item.suffix == suffix:
                return item
        raise ValueError(f"未找到时间维度: {suffix}")
    
    def __str__(self):
        return f"{self.name}(suffix={self.suffix})"
    
    def __repr__(self):
        return f"TimeframeEnum.{self.name}(suffix={self.suffix!r})"

