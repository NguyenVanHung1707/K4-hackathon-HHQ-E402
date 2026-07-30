import os
from functools import lru_cache
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseModel as BaseSettings
    class SettingsConfigDict:
        def __init__(self, **kwargs): pass


class Settings(BaseSettings):
    model_config = {"protected_namespaces": ()}
    app_name: str = "VLearn EduAI - Quiz & Analytics"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model_name: str = "gpt-4o-mini"
    temperature: float = 0.2


@lru_cache
def get_settings() -> Settings:
    return Settings()
