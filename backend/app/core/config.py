from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"

    database_url: str | None = None
    postgres_user: str = "courtops"
    postgres_password: str = "courtops_password"
    postgres_db: str = "courtops_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str = "change_this_in_real_usage"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434/v1/"
    ollama_model: str = "qwen3:8b"

    class Config:
        env_file = ".env"
        env_prefix = ""

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

