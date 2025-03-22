from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine

def init_db() -> None:
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def drop_db() -> None:
    """删除所有表"""
    Base.metadata.drop_all(bind=engine) 