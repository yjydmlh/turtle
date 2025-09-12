from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logger import db_logger

# 创建数据库引擎，启用连接池
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 自动检测连接是否有效
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_timeout=30,  # 连接池超时时间
    pool_recycle=3600,  # 连接回收时间（1小时）
    echo=settings.DEBUG,  # 在调试模式下打印SQL语句
    echo_pool=False,  # 不打印连接池日志
    connect_args={
        "connect_timeout": 10,  # 连接超时
        "application_name": "turtle_trading_system"
    }
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
        db_logger.debug("Creating new database session")
        yield db
    except Exception as e:
        db_logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db_logger.debug("Closing database session")
        db.close()