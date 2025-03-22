import os
import pathlib

# 创建主要目录结构
directories = [
    "app/api/v1",
    "app/core",
    "app/db",
    "app/models",
    "app/schemas",
    "app/services",
    "app/utils",
    "tests",
]

# 创建所有目录
for dir_path in directories:
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

# 创建必要的文件
files = [
    "requirements.txt",
    ".env",
    "README.md",
    "app/__init__.py",
    "app/api/__init__.py",
    "app/api/v1/__init__.py",
    "app/core/__init__.py",
    "app/db/__init__.py",
    "app/models/__init__.py",
    "app/schemas/__init__.py",
    "app/services/__init__.py",
    "app/utils/__init__.py",
]

for file_path in files:
    pathlib.Path(file_path).touch() 