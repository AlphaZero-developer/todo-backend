import os
from dataclasses import dataclass
from sqlalchemy import URL


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: URL
    REDIS_URL: str
    cache_ttl_seconds: int
    cache_tasks_key: str
    cors_allowed_origin: list[str]


def get_settings() -> Settings:
    return Settings(
        URL.create(
            "postgresql+psycopg",
            username="postgres",
            password=os.environ["POSTGRES_PASSWORD"],
            host="postgres",
            port=5432,
            database="postgres",
        ),
        REDIS_URL="redis://redis:6379/0",
        cache_ttl_seconds=3600,
        cache_tasks_key="cache:tasks_list",
        cors_allowed_origin=["http://localhost:3000"],
    )
