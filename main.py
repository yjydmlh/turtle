"""主应用文件"""
from myboot.core.application import create_app

app = create_app(name="turtle-front")

if __name__ == "__main__":
    app.run()
