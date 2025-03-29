from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
from app import crud
from app.schemas.user import UserCreate
from app.core.config import settings

def init_db(db: Session) -> None:
    """初始化数据库"""
    # 创建TimescaleDB扩展
    db.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    db.commit()

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 创建第一个超级用户
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
        )
        user = crud.user.create(db, obj_in=user_in)

def drop_db() -> None:
    """删除所有表"""
    Base.metadata.drop_all(bind=engine) 