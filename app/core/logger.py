import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 创建日志记录器
app_logger = logging.getLogger("app")
app_logger.setLevel(settings.LOG_LEVEL)

# 创建格式化器
formatter = logging.Formatter(settings.LOG_FORMAT)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(settings.LOG_LEVEL)
console_handler.setFormatter(formatter)

# 创建文件处理器
file_handler = RotatingFileHandler(
    filename=str(Path(settings.LOG_FILE)),
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10,
    encoding='utf-8'
)
file_handler.setLevel(settings.LOG_LEVEL)
file_handler.setFormatter(formatter)

# 添加处理器到日志记录器
app_logger.addHandler(console_handler)
app_logger.addHandler(file_handler)

# 设置其他模块的日志级别
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# 创建数据库日志记录器
db_logger = logging.getLogger("sqlalchemy.engine")
db_logger.setLevel(settings.LOG_LEVEL)
db_logger.addHandler(console_handler)
db_logger.addHandler(file_handler)