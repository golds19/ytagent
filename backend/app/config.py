from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    google_api_key: str = ""
    firecrawl_api_key: str = ""
    backend_url: str = "http://localhost:8000"
    allowed_origins: str = "http://localhost:8501,http://127.0.0.1:8501"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
