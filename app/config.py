from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_name: str = 'ShopEase API'
    environment: str = Field('development', description='deployment environment')
    api_key: SecretStr = Field(
        SecretStr('dev-local-api-key-123'),
        description='Required API key for privileged endpoints',
    )
    low_stock_threshold: int = 10

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {'development', 'staging', 'production', 'test'}
        if normalized not in allowed:
            msg = f"environment must be one of: {', '.join(sorted(allowed))}"
            raise ValueError(msg)
        return normalized

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, value: SecretStr, info) -> SecretStr:
        key = value.get_secret_value().strip()
        if len(key) < 16:
            raise ValueError('api_key must be at least 16 characters long')
        env = info.data.get('environment', 'development')
        if env in {'production', 'staging'} and key == 'dev-local-api-key-123':
            raise ValueError('default development API key is forbidden outside development/test')
        return SecretStr(key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
