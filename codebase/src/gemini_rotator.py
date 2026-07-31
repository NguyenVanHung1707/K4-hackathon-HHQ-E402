import json
import requests
import traceback
from typing import Dict, Any, List, Optional

try:
    from codebase.src.config import get_settings
    from codebase.src.local_llm import LocalLlamaService
except ImportError:
    try:
        from config import get_settings
        from local_llm import LocalLlamaService
    except ImportError:
        LocalLlamaService = None


# Official High-Speed Google Gemini Models Pool (Prioritizing Flash models for instant response)
GEMINI_MODELS_POOL = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
]


class GeminiMultiModelRotator:
    """Hệ thống gọi LLM Luân Phiên (Tự động hỗ trợ mô hình Local Llama-3.2-1B & Gemini API)."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.gemini_api_key
        self.current_model_idx = 0
        self.local_llm = LocalLlamaService() if LocalLlamaService else None

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Gọi LLM (Ưu tiên mô hình Local Llama-3.2-1B nếu bật USE_LOCAL_LLM, sau đó tới Gemini API)."""
        if self.settings.use_local_llm and self.local_llm:
            print(f"[LLM Engine] Running Local Model Llama-3.2-1B ({self.settings.local_model_path})...")
            local_res = self.local_llm.generate_json(prompt)
            if local_res:
                return local_res
            print("[LLM Engine] Local Model Llama-3.2-1B generation failed/skipped. Trying Gemini API...")

        if not self.api_key:
            print("[Gemini Rotator] GEMINI_API_KEY not found. Skipping Gemini...")
            if self.local_llm and not self.settings.use_local_llm:
                print("[LLM Engine] Fallback: Trying Local Llama-3.2-1B...")
                return self.local_llm.generate_json(prompt)
            return None

        retry_pool = GEMINI_MODELS_POOL
        max_attempts = len(retry_pool)

        for offset in range(max_attempts):
            model_name = retry_pool[(self.current_model_idx + offset) % len(retry_pool)]
            print(f"[Gemini Rotator ({offset+1}/{max_attempts})] Trying model: {model_name}...")

            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                body = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": self.settings.temperature,
                        "responseMimeType": "application/json"
                    }
                }
                # Ultra fast 4s timeout for real models
                res = requests.post(url, headers=headers, json=body, timeout=4)
                if res.status_code == 200:
                    res_data = res.json()
                    candidates = res_data.get("candidates", [])
                    if candidates and len(candidates) > 0:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            raw_text = parts[0]["text"]
                            clean_json = raw_text.replace("```json\n", "").replace("```", "").strip()
                            data = json.loads(clean_json)
                            print(f"[Gemini Rotator REST SUCCESS] Model {model_name} generated JSON in real-time!")
                            self.current_model_idx = (self.current_model_idx + offset) % len(retry_pool)
                            return data
                else:
                    print(f"[Gemini Rotator REST] {model_name} returned HTTP {res.status_code}")
            except Exception as e2:
                print(f"[Gemini Rotator REST Error] {model_name} attempt failed: {e2}")

        print("[Gemini Rotator] Gemini failover pool exhausted/busy. Switching to Dynamic RAG Engine...")
        return None
