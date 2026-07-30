import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings


class Settings(BaseSettings):
    model_config = {"protected_namespaces": ()}
    app_name: str = "VLearn EduAI - Quiz & Analytics Engine"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model_name: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    temperature: float = 0.2
    chroma_db_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chroma"))
    data_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
