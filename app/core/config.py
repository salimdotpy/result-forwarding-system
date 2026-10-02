from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Online Students' Result Forwarding Management System"
    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/result_forwarding"
    session_cookie: str = "result_forwarding_session"
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def max_upload_size(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
