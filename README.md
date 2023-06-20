# [Watchlist](https://github.com/helloflask/watchlist)的一个FastAPI实现

## 开始使用

### Poetry
```shell
poetry shell
poetry install
```

### pip
```shell
python -m venv env

# Windows PowerShell (cmd: env\Scripts\activate.bat)
env\Scripts\Activate.ps1
(env) pip install -r requirements.txt
```

## 环境变量
1. 复制 .env.example 为 .env
2. SECRET_KEY:
    ```shell
    python -c "import os; print(os.urandom(24).hex())"
    ```
3. DATABASE_URL: SQLAlchemy 支持的 URL

## 迁移
```shell
alembic upgrade head
```

## 测试
```shell
pytest tests\test.py
```

## 运行
```shell
uvicorn watchlist.main:app
```
