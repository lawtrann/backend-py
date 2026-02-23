from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Backend API"
    API_PORT: int = 8000
    DEBUG: bool = False

    # DB components (with dev defaults)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "example"
    POSTGRES_DB: str = "backend"
    DB_HOST: str = "localhost"
    DB_PORT: int = 15432
    DATABASE_URL: str = ""

    # DB connection pool
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = []
    COOKIE_SECURE: bool = False

    # MinIO / Object Storage
    MINIO_ENDPOINT: str = "localhost:9080"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_DEFAULT_BUCKET: str = "uploads"
    MINIO_PRESIGNED_URL_EXPIRY_SECONDS: int = 3600

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
            )
        return self


settings = Settings()
