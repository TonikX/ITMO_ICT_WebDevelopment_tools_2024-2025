from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from typing import Optional, Dict, List
import logging.config

# 加载 .env 文件，默认从项目根目录加载，若文件路径不同可指定 path 参数
load_dotenv()

class Settings(BaseSettings):
    # 数据库连接配置
    database_url: AnyUrl
    # JWT 相关配置
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "default_secret_key_should_be_changed")  # JWT 密钥，用于签名
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")  # JWT 加密算法，默认常用的 HS256
    jwt_token_expire_minutes: int = int(os.getenv("JWT_TOKEN_EXPIRE_MINUTES", 30))  # Token 过期时间，单位分钟

    # 日志配置
    log_config: Optional[Dict] = {  # 日志配置字典，可自定义日志格式、级别等
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "app.log",  # 日志文件存储路径，可根据需要调整
                "formatter": "default"
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO"  # 根日志级别，可根据开发/生产环境调整
        },
        "loggers": {
            "fastapi": {
                "level": "WARNING"  # 降低 FastAPI 框架自身日志级别，避免过多冗余日志
            },
            "sqlmodel": {
                "level": "WARNING"  # 调整 SQLModel 相关日志级别
            }
        }
    }

    # 其他自定义配置（示例：财务分类配置，可用于限定用户输入的收支分类）
    finance_categories: List[str] = ["餐饮", "购物", "交通", "娱乐", "通讯", "房租", "其他"]

    class Config:
        env_file = ".env"  # 指定 .env 文件位置，若在其他目录可修改，如 "config/.env"
        env_file_encoding = "utf-8"  # .env 文件编码

# 初始化配置实例
settings = Settings()

# 配置日志
if settings.log_config:
    logging.config.dictConfig(settings.log_config)

DATABASE_URL = settings.database_url