import sys
import os

# Thêm thư mục gốc vào PYTHONPATH để có thể import từ codebase
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codebase.src.api import teacher_materials

def run_seed():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    seed_flag_file = os.path.join(data_dir, ".seeded")

    if os.path.exists(seed_flag_file):
        print("[Skip Seed] Du lieu mau (Day01, Day02) da duoc khoi tao tu truoc. Bo qua buoc seeding!")
        return

    print("Bat dau khoi tao du lieu mau cho tat ca cac Day (Day01, Day02)...")
    
    # Identify all Day directories in data/
    day_folders = [d for d in sorted(os.listdir(data_dir)) if os.path.isdir(os.path.join(data_dir, d)) and d.startswith("Day")]
    if not day_folders:
        day_folders = ["Day01", "Day02"]

    for day in day_folders:
        day_path = os.path.join(data_dir, day)
        script_dir = os.path.join(day_path, "Script")
        transcript_content = ""

        if os.path.exists(script_dir):
            for file in sorted(os.listdir(script_dir)):
                if file.endswith(".md") or file.endswith(".txt"):
                    filepath = os.path.join(script_dir, file)
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            transcript_content += f"\n--- {file} ---\n" + f.read()
                    except Exception as e:
                        print(f"Loi doc file {filepath}: {e}")

        if not transcript_content.strip():
            if day == "Day01":
                transcript_content = """
                # Buoi 1: Nền tảng LLM, Transformer & Attention Mechanism
                Kiến trúc Transformer giới thiệu cơ chế Self-Attention cho phép mô hình tính toán mối tương quan giữa mọi từ trong câu.
                Positional Encoding giúp mô hình duy trì thứ tự từ trong chuỗi văn bản.
                Encoder mã hóa đầu vào thành vector ngữ nghĩa, còn Decoder sinh văn bản đầu ra.
                """
            else:
                transcript_content = """
                # Buoi 2: Nền tảng RAG, Vector Database & Embedding Models
                RAG (Retrieval-Augmented Generation) kết hợp khả năng tìm kiếm từ CSDL ngoài với khả năng sinh câu của LLM.
                Embedding Models biến đổi văn bản thô thành vector số trong không gian nhiều chiều.
                Vector Database (như ChromaDB) thực hiện tìm kiếm k-NN các đoạn văn bản có độ tương đồng ngữ nghĩa cao nhất.
                """

        day_num = day.replace("Day", "").strip()
        payload = {
            "target_day": day,
            "upload_mode": "overwrite",
            "transcript_text": transcript_content,
            "session_title": f"Buoi {day_num} ({day}): Hoc lieu nguyen ban & bai tap AI"
        }

        try:
            teacher_materials(payload)
            print(f"Seeding thanh cong du lieu cho {day}!")
        except Exception as e:
            print(f"Loi khi seeding cho {day}:", e)

    # Write flag file after seeding all days
    try:
        with open(seed_flag_file, "w", encoding="utf-8") as f:
            f.write("seeded=true\n")
        print("Hoan tat seeding cho tat ca cac Day!")
    except Exception as e:
        print("Loi ghi file flag .seeded:", e)

if __name__ == "__main__":
    run_seed()
