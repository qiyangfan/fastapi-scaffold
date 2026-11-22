from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """环境变量契约：缺失或非法时启动即失败（fail-fast）。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "production", "test"] = "development"
    port: int = 3000
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
