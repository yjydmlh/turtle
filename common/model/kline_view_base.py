"""
K线视图实体类
用于映射不同时间维度的聚合视图（5m, 15m, 1h等）
通过动态指定表名来查询不同的视图，查询结果直接映射到实体类对象（类似 MyBatis）
视图字段：id, bucket, open_time, close_time, open_price, high_price, low_price, close_price, volume
注意：视图没有 created_at 和 updated_at 字段
"""

from sqlalchemy import Column, DateTime

from common.model.kline_base import KlineBase


class KlineView(KlineBase):

    bucket = Column(
        DateTime,
        nullable=False,
        comment="时间桶"
    )

    
    def __repr__(self):
        return f"<KlineView(id={self.id}, bucket={self.bucket}, open_time={self.open_time})>"

