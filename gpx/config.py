from pydantic_settings import BaseSettings

__all__ = ["Settings", "settings"]

class Settings(BaseSettings):
    github_client_id: str
    github_client_secret: str
    session_secret_key: str
    debug: bool = False
    github_access_token_override: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
