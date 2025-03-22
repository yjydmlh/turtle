import typer
from app.db.init_db import init_db, drop_db

app = typer.Typer()

@app.command()
def init():
    """初始化数据库"""
    init_db()
    typer.echo("数据库初始化完成")

@app.command()
def drop():
    """删除所有表"""
    drop_db()
    typer.echo("数据库表已删除")

if __name__ == "__main__":
    app() 