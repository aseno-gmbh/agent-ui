from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    AZURE_API_URL: AnyUrl
    AZURE_API_KEY: SecretStr
    debug_mode: bool = False  # Default value

