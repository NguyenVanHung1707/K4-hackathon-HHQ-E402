import re
from typing import List, Dict, Any

try:
    from codebase.src.config import get_settings
except ImportError:
    from config import get_settings


class TranscriptDenoiser:
    """Lọc rác transcript bài giảng thô (LLM Denoising: Remove Off-topic)."""

    OFFTOPIC_PATTERNS = [
        r"chào lớp", r"xin chào mọi người", r"giao lưu một chút",
        r"nghỉ giải lao", r"điểm danh", r"quét mã qr", r"phát thẻ",
        r"thay pin", r"đổi mic", r"hỗ trợ kỹ thuật", r"em đi làm 18 năm",
        r"chúc mọi người", r"mọi người vỗ tay"
    ]

    def __init__(self):
        self.settings = get_settings()

    def denoise_transcript(self, raw_transcript: str) -> Dict[str, Any]:
        """Loại bỏ các thông tin ngoài lề và chuẩn hóa transcript thành nội dung tri thức sạch."""
        lines = raw_transcript.strip().split("\n")
        clean_lines = []
        removed_count = 0

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check for administrative markers or off-topic patterns
            if line_str.startswith("> **Quy ước:") or line_str.startswith("> **Xử lý:"):
                continue

            is_offtopic = any(re.search(pat, line_str, re.IGNORECASE) for pat in self.OFFTOPIC_PATTERNS)
            if is_offtopic:
                removed_count += 1
                continue

            clean_lines.append(line_str)

        cleaned_text = "\n".join(clean_lines)

        return {
            "status": "success",
            "original_lines": len(lines),
            "cleaned_lines": len(clean_lines),
            "removed_chatter_count": removed_count,
            "cleaned_transcript": cleaned_text
        }
