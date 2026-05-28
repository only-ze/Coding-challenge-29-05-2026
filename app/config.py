from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
 
    DATABASE_URL: str 
    PIPEFY_PIPE_ID: str 
    PIPEFY_TOKEN: str 
    PIPEFY_API_URL: str 
 
 
settings = Settings()