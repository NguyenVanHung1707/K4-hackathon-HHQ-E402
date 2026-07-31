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
    local_model_path: str = os.getenv("LOCAL_MODEL_PATH", r"e:\hung\VinAI\Model\Llama-3.2-1B")
    use_local_llm: bool = os.getenv("USE_LOCAL_LLM", "true").lower() in ("true", "1", "yes", "y")
    llm_model_name: str = os.getenv("LLM_MODEL", "Llama-3.2-1B")
    temperature: float = 0.2
    chroma_db_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/chroma"))
    data_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
