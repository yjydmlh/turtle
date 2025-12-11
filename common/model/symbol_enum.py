"""
交易品种枚举
每个枚举项包含品种名（如 btcusdt）和对应的表名（如 btc_usdt）
"""
from enum import Enum


class SymbolEnum(Enum):
    """交易品种枚举"""
    
    BTC_USDT = ("btcusdt", "btc_usdt")
    ETH_USDT = ("ethusdt", "eth_usdt")
    SOL_USDT = ("solusdt", "sol_usdt")
    
    def __new__(cls, symbol_name: str, table_name: str):
        """
        创建枚举项
        
        Args:
            symbol_name: 品种名（如 btcusdt）
            table_name: 对应的表名（如 btc_usdt）
        """
        obj = object.__new__(cls)
        obj._value_ = symbol_name  # 使用品种名作为 value
        obj.symbolName = symbol_name
        obj.tablePrefix = table_name
        return obj
    
    @property
    def code(self) -> str:
        """返回品种名（兼容性属性）"""
        return self.symbolName
    
    @classmethod
    def from_symbol_name(cls, symbol_name: str) -> "SymbolEnum":
        """
        根据品种名获取枚举项
        
        Args:
            symbol_name: 品种名（如 btcusdt）
        
        Returns:
            对应的枚举项
        
        Raises:
            ValueError: 如果找不到对应的枚举项
        """
        for item in cls:
            if item.symbolName == symbol_name:
                return item
        raise ValueError(f"未找到品种: {symbol_name}")
    
    @classmethod
    def from_table_name(cls, table_name: str) -> "SymbolEnum":
        """
        根据表名获取枚举项
        
        Args:
            table_name: 表名（如 btc_usdt）
        
        Returns:
            对应的枚举项
        
        Raises:
            ValueError: 如果找不到对应的枚举项
        """
        for item in cls:
            if item.tablePrefix == table_name:
                return item
        raise ValueError(f"未找到表名: {table_name}")
    
    def __str__(self):
        return f"{self.name}(symbol={self.symbolName}, table={self.tablePrefix})"
    
    def __repr__(self):
        return f"SymbolEnum.{self.name}(symbol={self.symbolName!r}, table={self.tablePrefix!r})"

