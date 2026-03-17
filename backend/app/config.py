from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ecommerce:ecommerce@localhost:5432/ecommerce"

    SECRET_KEY: str = "change-me-to-a-random-secret-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    RESERVATION_EXPIRE_MINUTES: int = 15
    RESERVATION_CLEANUP_INTERVAL_SECONDS: int = 120

    DEBUG: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
