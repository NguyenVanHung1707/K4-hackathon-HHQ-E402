import os
import sys
import json
import re
import traceback
from typing import Dict, Any, Optional

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


def safe_print(msg: str):
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode('ascii', errors='ignore').decode('ascii'))
        except Exception:
            pass


class LocalLlamaService:
    """Hệ thống chạy LLM Local Llama-3.2-1B trực tiếp trên GPU CUDA / CPU."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LocalLlamaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: Optional[str] = None):
        if self._initialized:
            return
        self.settings = get_settings()
        self.model_path = model_path or self.settings.local_model_path or r"e:\hung\VinAI\Model\Llama-3.2-1B"
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        self._initialized = True

    def load_model(self) -> bool:
        if self.is_loaded and self.model is not None:
            return True

        if not os.path.exists(self.model_path):
            safe_print(f"[Local LLM Error] Path does not exist: {self.model_path}")
            return False

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            use_cuda = torch.cuda.is_available()
            device = "cuda" if use_cuda else "cpu"
            gpu_name = torch.cuda.get_device_name(0) if use_cuda else "CPU"
            safe_print(f"[Local LLM] Loading Llama-3.2-1B on GPU: {gpu_name} (Device: {device.upper()})...")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
            if self.tokenizer.pad_token_id is None:
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

            torch_dtype = torch.float16 if use_cuda else torch.float32

            # Explicitly load model directly onto CUDA GPU if available
            if use_cuda:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch_dtype,
                    trust_remote_code=True
                ).to("cuda")
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype=torch_dtype,
                    trust_remote_code=True
                ).to("cpu")

            self.device = device
            self.is_loaded = True
            safe_print(f"[Local LLM GPU ACTIVE] Llama-3.2-1B running on {gpu_name} ({device.upper()})!")
            return True
        except ImportError as ie:
            safe_print(f"[Local LLM Warning] Missing PyTorch / Transformers: {ie}. Fallback to Dynamic Engine.")
            return False
        except Exception as e:
            safe_print(f"[Local LLM Load Error] Failed to load Llama-3.2-1B: {e}")
            traceback.print_exc()
            return False

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Sinh chuỗi JSON từ Llama-3.2-1B trên GPU."""
        if not self.load_model():
            return None

        try:
            import torch

            system_instruction = (
                "You are an AI assistant. Return response ONLY in valid JSON format. "
                "Do not include any explanation or extra text outside JSON."
            )

            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]

            if hasattr(self.tokenizer, "apply_chat_template"):
                try:
                    formatted_prompt = self.tokenizer.apply_chat_template(
                        messages, tokenize=False, add_generation_prompt=True
                    )
                except Exception:
                    formatted_prompt = f"System: {system_instruction}\nUser: {prompt}\nAssistant:"
            else:
                formatted_prompt = f"System: {system_instruction}\nUser: {prompt}\nAssistant:"

            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=False,
                    pad_token_id=self.tokenizer.pad_token_id
                )

            input_length = inputs.input_ids.shape[1]
            generated_tokens = outputs[0][input_length:]
            response_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

            # Parse JSON out of response
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                clean_json = json_match.group(1).strip()
            else:
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    clean_json = response_text[start:end+1].strip()
                else:
                    clean_json = response_text.strip()

            # Simple JSON repair for small model quirks
            try:
                # Remove python-style trailing comments if any
                clean_json = re.sub(r'#.*$', '', clean_json, flags=re.MULTILINE)
                # Fix trailing commas before closing braces/brackets
                clean_json = re.sub(r',\s*([\}\]])', r'\1', clean_json)
                # Replace potential smart quotes or other minor quoting issues
                clean_json = clean_json.replace('“', '"').replace('”', '"')
            except Exception:
                pass

            data = json.loads(clean_json)
            safe_print(f"[Local LLM GPU SUCCESS] Llama-3.2-1B generated JSON response on {self.device.upper()}!")
            return data
        except Exception as e:
            safe_print(f"[Local LLM Generation Warning] Llama-3.2-1B JSON generation fallback: {e}")
            return None
