from celery import Celery
from os import getenv

# 初始化 Celery（连接 Redis 作为 Broker）
celery_app = Celery(
    "lab3_worker",
    broker=getenv("REDIS_URL", "redis://localhost:6379/0"),  # 复用 Redis
    backend=getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.routers.tasks"]  # 任务模块路径
)

# Celery 配置（可选）
celery_app.conf.timezone = "UTC"
celery_app.conf.task_serializer = "json"