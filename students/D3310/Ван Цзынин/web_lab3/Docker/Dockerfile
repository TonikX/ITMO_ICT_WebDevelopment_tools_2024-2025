FROM python:3.9-slim

# 设置工作目录（容器内）
WORKDIR /app

# 复制依赖文件（从项目根目录复制 Requirements.txt 到容器 /app 目录）
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# 复制整个项目代码（从项目根目录复制到容器 /app 目录）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]