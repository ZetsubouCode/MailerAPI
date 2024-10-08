from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    sender_email: str

    class Config:
        env_file = ".env"


# Instantiate settings, so they can be used across the app
settings = Settings()