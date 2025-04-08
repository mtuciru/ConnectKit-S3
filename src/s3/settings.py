from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["settings", "Settings"]


class Settings(BaseSettings):
    """
    S3 module configuration.

    Loaded from environ (priority) and .env top-level file.
    Configuration of module depends on these settings.
    Frozen when module is loaded.
    """
    model_config = SettingsConfigDict(env_prefix="aws_",
                                      env_file='.env',
                                      env_file_encoding="utf-8",
                                      env_parse_none_str="",
                                      env_parse_enums=True,
                                      env_ignore_empty=False,
                                      extra="ignore",
                                      frozen=True,
                                      case_sensitive=False)
    host: str | None = None
    """
    S3 server host endpoint for default connection.
    
    Full URL for s3 server.
        
    Default: None
    """
    access_key_id: str | None = None
    """
    AWS_ACCESS_KEY_ID for default connection.

    See AWS_ACCESS_KEY_ID
    
    Default: None
    """
    secret_access_key: str | None = None
    """
    AWS_SECRET_ACCESS_KEY for default connection.
    
    See AWS_SECRET_ACCESS_KEY
        
    Default: None
    """
    region: str | None = None
    """
    AWS_REGION for default connection.
    
    See S3 REGION NAME
    
    Default: None
    """
    bucket: str | None = None
    """
    S3 bucket.
    
    Default S3 bucket if not specified in connection configuration.
    
    Default: None
    """


settings = Settings()
