import os
import sys
import subprocess
import time
import shutil
from pathlib import Path


class QuickStartManager:
    """缠论分析系统快速启动管理器"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.static_dir = self.project_root / "static"

    def setup(self):
        """设置项目环境"""
        print("🐢 缠论分析系统 - 快速启动")
        print("=" * 50)

        # 1. 检查Python版本
        self.check_python_version()

        # 2. 创建必要的目录
        self.create_directories()

        # 3. 检查数据库连接
        self.check_database()

        # 4. 检查Chan模块
        self.check_chan_module()

        # 5. 安装依赖（如果需要）
        self.check_dependencies()

        print("\n✅ 环境设置完成!")

    def check_python_version(self):
        """检查Python版本"""
        version = sys.version_info
        print(f"📋 检查Python版本: {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ 需要Python 3.8或更高版本")
            sys.exit(1)

        print("✅ Python版本符合要求")

    def create_directories(self):
        """创建必要的目录"""
        print("📁 创建项目目录...")

        directories = [
            "static",
            "logs",
            "data"
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"  ✅ {dir_name}/")

    def check_database(self):
        """检查数据库连接"""
        print("🗄️ 检查数据库连接...")

        try:
            from app.core.config import settings
            from app.db.session import engine

            # 尝试连接数据库
            with engine.connect() as conn:
                conn.execute("SELECT 1")

            print(f"  ✅ 数据库连接正常")

        except Exception as e:
            print(f"  ⚠️ 数据库连接失败: {str(e)}")
            print("  💡 请确保PostgreSQL服务正在运行，或检查DATABASE_URL配置")

            # 提供简单的数据库设置指导
            self.show_database_setup()

    def show_database_setup(self):
        """显示数据库设置指导"""
        print("\n📝 数据库设置指导:")
        print("1. 安装PostgreSQL")
        print("2. 创建数据库: CREATE DATABASE turtle;")
        print("3. 在.env文件中设置: DATABASE_URL=postgresql://user:password@localhost:5432/turtle")
        print("4. 配置PostgreSQL数据库连接: DATABASE_URL=postgresql://user:password@host:port/database")

    def check_chan_module(self):
        """检查Chan模块"""
        print("🧠 检查Chan模块...")

        try:
            from app.services.chan_adapter import chan_adapter

            info = chan_adapter.get_chan_info()
            if info['is_available']:
                print("  ✅ Chan模块集成正常")
            else:
                print("  ⚠️ Chan模块不可用，将使用简化分析")
                print("  💡 请运行: git submodule update --init")

        except Exception as e:
            print(f"  ⚠️ Chan模块检查失败: {str(e)}")

    def check_dependencies(self):
        """检查依赖包"""
        print("📦 检查依赖包...")

        required_packages = [
            'fastapi',
            'uvicorn',
            'sqlalchemy',
            'ccxt',
            'pandas'
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package}")

        if missing_packages:
            print(f"  💡 请运行: pip install {' '.join(missing_packages)}")
            print("  或者: pip install -r requirements.txt")
        else:
            print("  ✅ 所有依赖包已安装")

    def fetch_initial_data(self):
        """获取初始数据"""
        print("📊 获取初始K线数据...")

        try:
            from app.scripts.simple_fetch_data import SimpleBinanceDataFetcher

            fetcher = SimpleBinanceDataFetcher()

            # 先测试连接
            if not fetcher.test_connection():
                print("  ❌ 币安API连接失败")
                return False

            # 获取最近24小时数据
            success = fetcher.fetch_recent_data(hours=24)

            if success:
                print("  ✅ 初始数据获取成功")
                return True
            else:
                print("  ⚠️ 初始数据获取失败，稍后可在Web界面手动获取")
                return False

        except Exception as e:
            print(f"  ⚠️ 数据获取失败: {str(e)}")
            print("  💡 可以稍后在Web界面点击'获取新数据'按钮")
            return False

    def start_server(self):
        """启动服务器"""
        print("\n🚀 启动缠论分析系统...")

        try:
            import uvicorn
            from app.core.config import settings

            print(f"📍 系统启动信息:")
            print(f"   🌐 API服务: http://localhost:{settings.PORT}")
            print(f"   📚 API文档: http://localhost:{settings.PORT}/api/v1/docs")
            print(f"   🔍 健康检查: http://localhost:{settings.PORT}/health")

            # 检查前端是否可用
            frontend_available = (self.static_dir / "index.html").exists()
            if frontend_available:
                print(f"   🎨 Web界面: http://localhost:{settings.PORT}")
            else:
                print(f"   🎨 Web界面: 前端未构建，请访问API文档")

            print(f"\n📊 API接口:")
            print(f"   GET  /api/v1/simple/klines          # 获取K线数据")
            print(f"   POST /api/v1/simple/fetch-data      # 获取新数据")
            print(f"   GET  /api/v1/chan/analyze           # 缠论分析")
            print(f"   GET  /api/v1/chan/chart-data        # 图表数据")

            print(f"\n🎯 使用方法:")
            print(f"   1. 点击'获取新数据'从币安获取最新K线")
            print(f"   2. 选择时间周期查看聚合数据")
            print(f"   3. 执行缠论分析识别分型和笔")
            print(f"   4. 查看交易建议和市场状态")

            print(f"\n🔧 缠论功能:")
            print(f"   🔺 自动识别顶分型")
            print(f"   🔻 自动识别底分型")
            print(f"   📈 构建上涨笔和下跌笔")
            print(f"   📊 分析趋势方向和强度")
            print(f"   💡 生成操作建议")

            print(f"\n📋 按Ctrl+C停止服务器")
            print("=" * 50)

            # 询问是否获取初始数据
            try:
                response = input("\n🤔 是否现在获取初始数据? (y/N): ").lower().strip()
                if response in ['y', 'yes', '是']:
                    self.fetch_initial_data()
            except (EOFError, KeyboardInterrupt):
                print("\n⏭️ 跳过数据获取")

            print(f"\n🚀 启动服务器...")

            # 启动服务器
            uvicorn.run(
                "app.main:app",
                host=settings.HOST,
                port=settings.PORT,
                reload=False,  # 生产环境关闭热重载
                log_level="info"
            )

        except KeyboardInterrupt:
            print("\n\n👋 缠论分析系统已停止")
        except Exception as e:
            print(f"\n❌ 启动失败: {str(e)}")
            print("\n💡 可能的解决方案:")
            print("1. 检查端口是否被占用")
            print("2. 检查数据库连接配置")
            print("3. 确保所有依赖已安装")
            sys.exit(1)


def main():
    """主函数"""
    try:
        manager = QuickStartManager()

        # 设置环境
        manager.setup()

        # 询问是否立即启动
        while True:
            try:
                choice = input("\n🚀 是否现在启动系统? (y/n): ").lower().strip()
                if choice in ['y', 'yes', '是']:
                    manager.start_server()
                    break
                elif choice in ['n', 'no', '否']:
                    print("\n💡 稍后可运行以下命令启动系统:")
                    print("   python quick_start.py")
                    print("   或者: python run.py")
                    break
                else:
                    print("请输入 y 或 n")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 退出启动程序")
                break

    except Exception as e:
        print(f"\n❌ 启动脚本执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()