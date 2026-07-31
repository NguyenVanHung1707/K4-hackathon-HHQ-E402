# Reflection cá nhân — Nguyễn Văn Hưng (Mã HV: 2A202601284)

## Vai trò và phần công việc đảm nhận

Tôi là trưởng nhóm, đồng thời phụ trách AI Spec và Generator Engine. Công việc chính của tôi gồm xây dựng `spec.md`; thiết kế prompt và phát triển `codebase/src/generator.py` để sinh câu hỏi trắc nghiệm, điền khuyết và tự luận ngắn có trích dẫn; đồng thời phối hợp xây dựng Golden Set 20 test case.

## AI đã hỗ trợ tôi như thế nào

Tôi sử dụng Claude Code và Antigravity IDE để gợi ý cấu trúc Pydantic schema, tạo dữ liệu mock và rà soát System Prompt. AI còn đóng vai trò phản biện, giúp tìm các tình huống có thể hallucinate, sinh sai loại câu hỏi hoặc không bám transcript. Tôi đối chiếu các đề xuất với schema, transcript và Golden Set trước khi đưa vào hệ thống.

## Case fail và bài học rút ra

Trong cả hai lượt Eval, hệ thống đạt 17/20 case, tương đương 85%. Ba case `CASE-03`, `CASE-07` và `CASE-10` đều yêu cầu dạng `short_answer`, nhưng Generator chưa tạo được đầu ra đúng tiêu chí. Kết quả không thay đổi sau hai lượt cho thấy chỉ tối ưu prompt là chưa đủ; hệ thống còn cần bước kiểm tra có cấu trúc sau khi LLM sinh nội dung.

Bài học lớn nhất của tôi là không nên coi đầu ra của LLM là kết quả cuối cùng. Ngoài strict grounding, Generator phải xác thực `question_type`, schema, nội dung kỳ vọng và trích dẫn. Nếu đầu ra không đạt, hệ thống cần sinh lại hoặc báo lỗi rõ ràng. Eval không chỉ chứng minh sản phẩm hoạt động mà còn chỉ ra chính xác phần kiến trúc cần cải tiến.
