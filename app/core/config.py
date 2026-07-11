from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用
    app_name: str = "EcoMarket"
    debug: bool = True
    secret_key: str = "your-secret-key"

    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root123"
    mysql_database: str = "ecomarket"

    # openGauss
    opengauss_host: str = "localhost"
    opengauss_port: int = 5432
    opengauss_user: str = "opengauss_user"
    opengauss_password: str = "og123"
    opengauss_database: str = "ecomarket"

    # 数据库策略: primary | fallback | opengauss_only | sqlite
    db_strategy: str = "sqlite"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 1

    # Qwen3.7-Plus
    dashscope_api_key: str = ""

    # JWT
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # 文件上传
    upload_dir: str = "./uploads"
    max_upload_size: int = 5242880

    @property
    def mysql_database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )

    @property
    def opengauss_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.opengauss_user}:{self.opengauss_password}"
            f"@{self.opengauss_host}:{self.opengauss_port}/{self.opengauss_database}"
        )

    @property
    def sqlite_database_url(self) -> str:
        return "sqlite+aiosqlite:///./ecomarket.db"

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
