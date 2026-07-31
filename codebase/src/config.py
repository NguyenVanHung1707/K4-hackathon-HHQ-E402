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
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "20"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "0"))
    temperature: float = 0.2
    chroma_db_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chroma"))
    chroma_server_host: str = os.getenv("CHROMA_SERVER_HOST", "")
    chroma_server_port: int = int(os.getenv("CHROMA_SERVER_PORT", "8000"))
    data_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
