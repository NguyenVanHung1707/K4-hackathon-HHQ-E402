import json
import requests
import traceback
from typing import Dict, Any, List, Optional

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


# Comprehensive Curated Gemini Models List including Gemini 3.5, 3.1, 3.0 & 2.5 (Excluding TTS)
GEMINI_MODELS_POOL = [
    # Gemini 3.x Series
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-pro",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-live",
    "gemini-3-flash",
    "gemini-3.0-flash",
    "gemini-3.0-pro",
    "models/gemini-3.5-flash-lite",
    "models/gemini-3.5-flash",
    "models/gemini-3.1-pro",
    "models/gemini-3.1-flash-lite",
    "models/gemini-3-flash-live",
    "models/gemini-3-flash",
    "models/gemini-3.0-flash",
    "models/gemini-3.0-pro",
    # Gemini 2.5 & 2.0 Series
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-thinking-exp-01-21",
    "gemini-1.0-pro",
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    "models/gemini-2.0-flash",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemma-4-26b-a4b-it",
    "models/gemma-4-31b-it"
]


class GeminiMultiModelRotator:
    """Hệ thống gọi LLM Google Gemini luân phiên TOÀN BỘ MÔ HÌNH HỢP LỆ (Dynamic Multi-Model Failover Rotator, trừ TTS)."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.gemini_api_key
        self.current_model_idx = 0
        self._discovered_models: List[str] = []
        self._discover_all_models()

    def _discover_all_models(self):
        """Khám phá tự động toàn bộ mô hình Gemini khả dụng cho API Key này (loại trừ TTS)."""
        if not self.api_key:
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            all_api_models = []
            for m in genai.list_models():
                # Filter out TTS (Text-to-Speech) and Audio-only models
                if "tts" in m.name.lower() or "audio" in m.name.lower():
                    continue

                if "generateContent" in m.supported_generation_methods:
                    name_clean = m.name.replace("models/", "")
                    if name_clean not in all_api_models:
                        all_api_models.append(name_clean)
                    if m.name not in all_api_models:
                        all_api_models.append(m.name)

            if all_api_models:
                print(f"[Gemini Rotator] Discovered {len(all_api_models)} available Gemini text models (excluding TTS)!")
                self._discovered_models = all_api_models
        except Exception as e:
            print(f"[Gemini Rotator] Could not list models: {e}. Using fallback model list...")

    def get_active_pool(self) -> List[str]:
        """Tạo danh sách pool tổng hợp duy nhất từ cả khám phá tự động lẫn danh sách định sẵn (loại trừ TTS)."""
        combined = []
        for m in self._discovered_models:
            if "tts" not in m.lower() and "audio" not in m.lower() and m not in combined:
                combined.append(m)
        for m in GEMINI_MODELS_POOL:
            if "tts" not in m.lower() and "audio" not in m.lower() and m not in combined:
                combined.append(m)
        return combined if combined else [m for m in GEMINI_MODELS_POOL if "tts" not in m.lower()]

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Gọi Google Gemini luân phiên (tối đa 3 mô hình nhanh nhất với timeout 4s)."""
        if not self.api_key:
            print("[Gemini Rotator] GEMINI_API_KEY not found. Skipping Gemini...")
            return None

        active_pool = self.get_active_pool()
        # Prioritize top fast models: gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-flash
        fast_priority_models = [m for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"] if m in active_pool]
        retry_pool = fast_priority_models + [m for m in active_pool if m not in fast_priority_models]

        max_attempts = min(3, len(retry_pool))

        for offset in range(max_attempts):
            model_name = retry_pool[(self.current_model_idx + offset) % len(retry_pool)]
            print(f"[Gemini Rotator ({offset+1}/{max_attempts})] Trying model: {model_name}...")

            # Direct Google REST API Endpoint (Fast 4s Timeout)
            try:
                clean_model_name = model_name.replace("models/", "")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model_name}:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                body = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": self.settings.temperature,
                        "responseMimeType": "application/json"
                    }
                }
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
                            print(f"[Gemini Rotator REST SUCCESS] Model {model_name} generated JSON!")
                            self.current_model_idx = (self.current_model_idx + offset + 1) % len(retry_pool)
                            return data
                else:
                    print(f"[Gemini Rotator REST] {model_name} returned HTTP {res.status_code}")
            except Exception as e2:
                print(f"[Gemini Rotator REST Error] {model_name} attempt failed: {e2}")

        print("[Gemini Rotator] Gemini failover pool exhausted/busy. Switching to Dynamic RAG Engine...")
        return None
