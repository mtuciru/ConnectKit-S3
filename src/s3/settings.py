from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    AWS_HOST: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_BUCKET: Optional[str] = None


settings = Settings()
