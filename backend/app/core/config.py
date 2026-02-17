from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"

    postgres_user: str = "courtops"
    postgres_password: str = "courtops_password"
    postgres_db: str = "courtops_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str = "change_this_in_real_usage"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()

