from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.core.logger import app_logger

class AppException(HTTPException):
    """基础应用异常类"""
    def __init__(self, code: int, message: str, status_code: int = 400):
        super().__init__(status_code=status_code)
        self.code = code
        self.message = message

# 系统级异常 (1000-1999)
class SystemException(AppException):
    """系统级异常 (1000-1999)"""
    def __init__(self, code: int, message: str):
        super().__init__(code=code, message=message, status_code=500)

class DatabaseException(SystemException):
    """数据库异常"""
    def __init__(self, message: str):
        super().__init__(code=1001, message=message)

class ConfigException(SystemException):
    """配置异常"""
    def __init__(self, message: str):
        super().__init__(code=1002, message=message)

# 业务级异常 (2000-2999)
class BusinessException(AppException):
    """业务级异常 (2000-2999)"""
    def __init__(self, code: int, message: str):
        super().__init__(code=code, message=message, status_code=400)

class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(self, message: str):
        super().__init__(code=2002, message=message, status_code=404)

class InvalidParameterException(BusinessException):
    """无效参数异常"""
    def __init__(self, message: str):
        super().__init__(code=2001, message=message)

# 数据验证异常 (3000-3999)
class ValidationException(AppException):
    """数据验证异常 (3000-3999)"""
    def __init__(self, message: str):
        super().__init__(code=3000, message=message, status_code=422)

# 权限认证异常 (4000-4999)
class AuthenticationException(AppException):
    """认证异常 (4000-4999)"""
    def __init__(self, message: str):
        super().__init__(code=4000, message=message, status_code=401)

class AuthorizationException(AppException):
    """授权异常"""
    def __init__(self, message: str):
        super().__init__(code=4001, message=message, status_code=403)

# 第三方服务异常 (5000-5999)
class ExternalServiceException(AppException):
    """外部服务异常 (5000-5999)"""
    def __init__(self, message: str):
        super().__init__(code=5000, message=message, status_code=503)

def create_error_response(code: int, message: str, status_code: int = 400) -> JSONResponse:
    """创建统一的错误响应"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "code": code,
            "message": message,
            "data": None
        }
    )

def create_success_response(data: any = None, message: str = "success") -> JSONResponse:
    """创建统一的成功响应"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "code": 0,
            "message": message,
            "data": data
        }
    )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理应用异常"""
    app_logger.error(f"Application error: {exc.message}", exc_info=True)
    return create_error_response(exc.code, exc.message, exc.status_code)

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """处理数据库异常"""
    app_logger.error(f"Database error: {str(exc)}", exc_info=True)
    return create_error_response(1001, "数据库操作失败", 500)

async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """处理数据验证异常"""
    app_logger.error(f"Validation error: {str(exc)}", exc_info=True)
    return create_error_response(3000, "数据验证失败", 422)

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理通用异常"""
    app_logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return create_error_response(1000, "服务器内部错误", 500) 