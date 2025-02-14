# 使用 Python 3.11 的官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装 MySQL Client CLI
RUN apt-get update && apt-get install -y default-mysql-client

# 安装 Poetry
RUN pip install poetry

# 拷贝 Poetry 配置文件
COPY pyproject.toml poetry.lock /app/

# 安装依赖
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# 拷贝项目文件
COPY . /app


# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]