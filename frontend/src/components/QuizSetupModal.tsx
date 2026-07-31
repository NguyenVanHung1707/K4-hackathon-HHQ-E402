import React, { useState } from 'react';

interface QuestionTypeConfig {
  id: string;
  type: 'multiple_choice' | 'fill_in_blank' | 'short_essay';
  count: number;
}

interface QuizSetupModalProps {
  isOpen: boolean;
  sessionTitle: string;
  sessionId: string;
  studentId?: string;
  onClose: () => void;
  onStartQuiz: (quizData: any, setupParams: any) => void;
}

export const QuizSetupModal: React.FC<QuizSetupModalProps> = ({
  isOpen,
  sessionTitle,
  sessionId,
  studentId = '2012345',
  onClose,
  onStartQuiz,
}) => {
  // Default to exactly 3 questions total (1 Trắc nghiệm, 1 Điền từ, 1 Tự luận = 3 câu)
  const [configs, setConfigs] = useState<QuestionTypeConfig[]>([
    { id: '1', type: 'multiple_choice', count: 1 },
    { id: '2', type: 'fill_in_blank', count: 1 },
    { id: '3', type: 'short_essay', count: 1 },
  ]);

  const [difficulty, setDifficulty] = useState<string>('Cơ bản');
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const totalQuestions = configs.reduce((sum, item) => sum + item.count, 0);

  const handleAddType = () => {
    const nextType: 'multiple_choice' | 'fill_in_blank' | 'short_essay' =
      configs.length === 0
        ? 'multiple_choice'
        : configs.length === 1
        ? 'fill_in_blank'
        : 'short_essay';

    setConfigs([
      ...configs,
      { id: Date.now().toString(), type: nextType, count: 1 },
    ]);
  };

  const handleRemoveType = (id: string) => {
    setConfigs(configs.filter((c) => c.id !== id));
  };

  const handleUpdateType = (id: string, field: 'type' | 'count', value: any) => {
    setConfigs(
      configs.map((c) => (c.id === id ? { ...c, [field]: value } : c))
    );
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return 'Trắc nghiệm (Multiple Choice)';
      case 'fill_in_blank':
        return 'Điền từ / Điền khuyết (Fill in Blank)';
      case 'short_essay':
        return 'Tự luận ngắn (Short Essay)';
      default:
        return 'Trắc nghiệm';
    }
  };

  const handleTriggerGenerate = async () => {
    if (totalQuestions <= 0) {
      setErrorMsg('Vui lòng chọn ít nhất 1 câu hỏi!');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const typeCountsBreakdown: Record<string, number> = {};
    const summaryParts: string[] = [];

    configs.forEach((item) => {
      typeCountsBreakdown[item.type] = (typeCountsBreakdown[item.type] || 0) + item.count;
      summaryParts.push(`${item.count} ${getTypeLabel(item.type).split(' ')[0]}`);
    });

    const quizTypesStr = summaryParts.join(', ');
    const validSessionId = sessionId && sessionId !== 'undefined' ? sessionId : 'Day01';

    try {
      const res = await fetch(`/api/student/session/${validSessionId}/generate-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          num_questions: totalQuestions,
          quiz_types: quizTypesStr,
          type_counts: typeCountsBreakdown,
          difficulty_level: difficulty,
        }),
      });

      if (!res.ok) {
        let errorDetail = '';
        try {
          const errData = await res.json();
          errorDetail = errData.detail;
        } catch {}
        
        setLoading(false);
        setErrorMsg(errorDetail || `Lỗi máy chủ (${res.status}): Không thể sinh bài tập.`);
        return;
      }

      const data = await res.json();
      setLoading(false);
      onStartQuiz(data, { numQuestions: totalQuestions, quizTypes: quizTypesStr, difficulty });
    } catch {
      setLoading(false);
      setErrorMsg('Không thể kết nối đến Backend Server (http://localhost:8000). Vui lòng kiểm tra lại server đã được chạy chưa!');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="bg-white rounded-3xl shadow-2xl border border-[#c5c5d4] max-w-lg w-full p-6 md:p-8 relative">
        {/* Modal Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <span className="font-label-caps text-xs text-[#0f2a90] bg-[#2e44a7]/10 px-3 py-1 rounded-full font-semibold">
              CẤU HÌNH BÀI TẬP CHỦ ĐỘNG (MSSV: {studentId})
            </span>
            <h2 className="font-display-lg text-2xl font-bold text-[#0b1c30] mt-2">
              {sessionTitle}
            </h2>
            <p className="font-body-md text-xs text-[#757684]">
              Tự chọn dạng câu hỏi và số lượng để AI sinh bài tập theo đúng nhu cầu của bạn.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[#757684] hover:text-[#0b1c30] rounded-full hover:bg-[#eff4ff] transition-colors cursor-pointer"
          >
            <span className="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        {/* 403 Error Alert */}
        {errorMsg && (
          <div className="mb-6 p-4 bg-[#ffdad6] text-[#93000a] text-xs font-mono font-bold rounded-xl border border-[#ba1a1a]">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Setup Form Controls */}
        <div className="space-y-6">
          {/* Dynamic Question Type Builder */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="font-headline-md text-xs font-semibold text-[#0b1c30]">
                1. CHỌN DẠNG CÂU HỎI & SỐ LƯỢNG YÊU CẦU:
              </label>
              <span className="font-mono text-xs font-bold text-[#0f2a90] bg-[#eff4ff] px-2.5 py-1 rounded-full">
                Tổng: {totalQuestions} câu
              </span>
            </div>

            {/* List of Dynamic Type Rows */}
            <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
              {configs.map((item, idx) => (
                <div
                  key={item.id}
                  className="flex items-center gap-2 bg-[#f8f9ff] p-3 rounded-2xl border border-[#c5c5d4]"
                >
                  <span className="font-bold text-xs text-[#0f2a90] w-5">#{idx + 1}</span>

                  {/* Select Type */}
                  <select
                    value={item.type}
                    onChange={(e) =>
                      handleUpdateType(
                        item.id,
                        'type',
                        e.target.value as 'multiple_choice' | 'fill_in_blank' | 'short_essay'
                      )
                    }
                    className="flex-1 p-2 bg-white border border-[#c5c5d4] rounded-xl text-xs font-semibold text-[#0b1c30] focus:border-[#0f2a90] outline-none"
                  >
                    <option value="multiple_choice">Trắc nghiệm (Multiple Choice)</option>
                    <option value="fill_in_blank">Điền từ / Điền khuyết (Fill in Blank)</option>
                    <option value="short_essay">Tự luận ngắn (Short Essay)</option>
                  </select>

                  {/* Input Count */}
                  <div className="flex items-center gap-1 bg-white border border-[#c5c5d4] rounded-xl p-1">
                    <button
                      type="button"
                      onClick={() =>
                        handleUpdateType(
                          item.id,
                          'count',
                          Math.max(1, item.count - 1)
                        )
                      }
                      className="w-6 h-6 text-xs font-bold text-[#0f2a90] hover:bg-[#eff4ff] rounded flex items-center justify-center cursor-pointer"
                    >
                      -
                    </button>
                    <input
                      type="number"
                      min={1}
                      max={20}
                      value={item.count}
                      onChange={(e) =>
                        handleUpdateType(
                          item.id,
                          'count',
                          Math.max(1, parseInt(e.target.value) || 1)
                        )
                      }
                      className="w-8 text-center text-xs font-bold font-mono text-[#0b1c30] outline-none"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        handleUpdateType(item.id, 'count', item.count + 1)
                      }
                      className="w-6 h-6 text-xs font-bold text-[#0f2a90] hover:bg-[#eff4ff] rounded flex items-center justify-center cursor-pointer"
                    >
                      +
                    </button>
                  </div>

                  {/* Remove Row Button */}
                  <button
                    type="button"
                    onClick={() => handleRemoveType(item.id)}
                    className="p-1.5 text-[#ba1a1a] hover:bg-[#ffdad6] rounded-xl transition-colors cursor-pointer"
                    title="Xóa dạng câu hỏi này"
                  >
                    <span className="material-symbols-outlined text-sm">delete</span>
                  </button>
                </div>
              ))}
            </div>

            {/* Add More Type Button */}
            <button
              type="button"
              onClick={handleAddType}
              className="mt-3 w-full py-2.5 border-2 border-dashed border-[#0f2a90] text-[#0f2a90] rounded-2xl font-label-caps text-xs font-bold hover:bg-[#eff4ff] transition-all flex items-center justify-center gap-1 cursor-pointer"
            >
              <span className="material-symbols-outlined text-sm">add</span>
              Thêm dạng câu hỏi khác
            </button>
          </div>

          {/* 2. Mức độ khó */}
          <div>
            <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-2">
              2. MỨC ĐỘ KHÓ YÊU CẦU:
            </label>
            <div className="grid grid-cols-2 gap-3">
              {['Cơ bản', 'Nâng cao'].map((d) => (
                <button
                  key={d}
                  onClick={() => setDifficulty(d)}
                  className={`py-3 rounded-2xl border-2 font-bold text-xs transition-all cursor-pointer ${
                    difficulty === d
                      ? 'border-[#0f2a90] bg-[#eff4ff] text-[#0f2a90] shadow-sm'
                      : 'border-[#c5c5d4] text-[#454652] hover:border-[#0f2a90]/40'
                  }`}
                >
                  {d === 'Cơ bản' ? '🌱 Cơ bản (Foundation)' : '🔥 Nâng cao (Advanced)'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-8 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-5 py-3 border border-[#c5c5d4] rounded-full text-xs font-semibold text-[#454652] hover:bg-[#eff4ff] cursor-pointer"
          >
            Hủy
          </button>
          <button
            onClick={handleTriggerGenerate}
            disabled={loading}
            className="flex-1 bg-[#006c49] text-white py-3 rounded-full font-label-caps text-xs font-bold shadow-md hover:bg-[#006c49]/90 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <span className="material-symbols-outlined text-sm animate-spin">refresh</span>
                AI đang sinh đề thời gian thực...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-sm">sparkles</span>
                Tạo {totalQuestions} bài tập & Bắt đầu
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
