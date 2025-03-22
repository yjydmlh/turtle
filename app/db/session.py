from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logger import db_logger

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 自动检测连接是否有效
    pool_size=5,         # 连接池大小
    max_overflow=10,     # 最大溢出连接数
    echo=settings.DEBUG  # 在调试模式下打印SQL语句
)

# 设置默认schema为public
@event.listens_for(engine, 'connect')
def set_search_path(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('SET search_path TO public')
    cursor.close()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        db_logger.info("Creating new database session")
        yield db
    finally:
        db_logger.info("Closing database session")
        db.close() 