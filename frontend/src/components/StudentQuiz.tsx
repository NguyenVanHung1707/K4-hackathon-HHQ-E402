import React, { useState, useEffect } from 'react';
import { QuizSetupModal } from './QuizSetupModal';

interface StudentQuizProps {
  quizId: string;
  studentProfile: { studentId?: string; fullName?: string };
  onBackToPath: () => void;
  onSelectSession?: (sessionId: string) => void;
}

export const StudentQuiz: React.FC<StudentQuizProps> = ({
  quizId,
  studentProfile,
  onBackToPath,
  onSelectSession,
}) => {
  const [quizData, setQuizData] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [gradingResult, setGradingResult] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [forbiddenMsg, setForbiddenMsg] = useState<string | null>(null);

  // Setup Modal State
  const [setupModalOpen, setSetupModalOpen] = useState<boolean>(false);

  // Sidebar Progress State
  const [progressList, setProgressList] = useState<any[]>([]);

  const fetchStudentProgress = () => {
    const sId = studentProfile.studentId || '2012345';
    fetch(`/api/student/progress?student_id=${sId}&t=${Date.now()}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.progress) setProgressList(data.progress);
      })
      .catch((err) => console.log('Error fetching progress for sidebar:', err));
  };

  useEffect(() => {
    fetchStudentProgress();
  }, [quizId, studentProfile]);

  useEffect(() => {
    setForbiddenMsg(null);
    setSubmitted(false);
    setGradingResult(null);
    setAnswers({});

    fetch(`/api/student/session/${quizId}/quiz?student_id=${studentProfile.studentId || '2012345'}`)
      .then(async (res) => {
        if (res.status === 403) {
          const errData = await res.json();
          setForbiddenMsg(errData.detail || '403 Forbidden: Yêu cầu hoàn thành bài tập của buổi học trước!');
          return null;
        }
        return res.json();
      })
      .then((data) => {
        if (data) setQuizData(data);
      })
      .catch((err) => console.log('Error loading quiz:', err));
  }, [quizId, studentProfile]);

  const handleSelectAnswer = (qId: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [qId]: value }));
  };

  const handleApplySetup = async (setupConfig: { num_questions: number; quiz_types: string; difficulty_level: string }) => {
    try {
      const response = await fetch(`/api/student/session/${quizId}/generate-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentProfile.studentId || '2012345',
          ...setupConfig,
        }),
      });

      const data = await response.json();
      if (data && data.questions) {
        setQuizData(data);
        setSubmitted(false);
        setGradingResult(null);
        setAnswers({});
      }
    } catch (err) {
      console.error('Error generating quiz:', err);
    }
  };

  const handleSubmitQuiz = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch(`/api/student/session/${quizId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentProfile.studentId || '2012345',
          student_name: studentProfile.fullName || 'Nguyễn Văn A',
          transcript_id: quizId,
          answers: answers,
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setGradingResult(data.grading_result);
        setSubmitted(true);
        fetchStudentProgress();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err) {
      console.error('Error submitting quiz:', err);
      setSubmitted(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentQuestions = quizData?.questions || [];

  return (
    <div className="bg-[#f8f9ff] text-[#0b1c30] min-h-screen font-body-md flex flex-col">
      {/* Top Navigation */}
      <header className="sticky top-0 z-40 bg-white shadow-sm border-b border-[#e5eeff] px-4 md:px-10 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBackToPath}
            className="flex items-center gap-2 text-[#454652] hover:text-[#0f2a90] text-xs font-label-caps cursor-pointer"
          >
            <span className="material-symbols-outlined text-sm">arrow_back</span>
            Bản đồ Bài học
          </button>
          <span className="font-display-lg text-xl font-bold text-[#0f2a90]">
            VLearn Student Portal — {quizId}
          </span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setSetupModalOpen(true)}
            className="bg-[#eff4ff] text-[#0f2a90] border border-[#2e44a7]/40 px-3.5 py-1.5 rounded-full font-label-caps text-xs font-semibold hover:bg-[#dce9ff] transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
          >
            <span className="material-symbols-outlined text-sm">tune</span>
            Tạo thêm / Cấu hình lại
          </button>
          <div className="font-label-caps text-xs text-[#0f2a90] bg-[#2e44a7]/10 px-3.5 py-1.5 rounded-full font-semibold">
            Tổng số: {currentQuestions.length} câu hỏi
          </div>
        </div>
      </header>

      {/* Main Layout Container with Left Sidebar */}
      <div className="flex flex-1">
        {/* LEFT SIDEBAR NAVIGATION FOR SESSIONS / DAYS */}
        <aside className="hidden md:flex flex-col w-[260px] bg-white border-r border-[#c5c5d4] p-4 gap-2">
          <div className="px-3 py-3 mb-2 border-b border-[#e5eeff]">
            <div className="flex items-center gap-2 mb-1">
              <span className="material-symbols-outlined text-[#0f2a90]">menu_book</span>
              <h2 className="font-headline-md text-sm font-bold text-[#0b1c30]">Danh Sách Buổi Học</h2>
            </div>
            <p className="font-label-caps text-[10px] text-[#757684]">
              MSSV: <span className="font-bold text-[#0f2a90]">{studentProfile.studentId || '2012345'}</span>
            </p>
          </div>

          {/* List of Day Sessions */}
          <div className="space-y-2 flex-1">
            {progressList.length > 0 ? (
              progressList.map((item) => {
                const isCurrent = item.module_id === quizId;
                const isCompleted = item.status === 'completed';
                const isLocked = item.status === 'locked';

                return (
                  <button
                    key={item.module_id}
                    disabled={isLocked}
                    onClick={() => {
                      if (!isLocked && onSelectSession) {
                        onSelectSession(item.module_id);
                      }
                    }}
                    className={`w-full p-3 rounded-2xl text-left transition-all flex items-center justify-between cursor-pointer ${
                      isCurrent
                        ? 'bg-[#2e44a7] text-white shadow-md font-bold'
                        : isCompleted
                        ? 'bg-[#6cf8bb]/20 text-[#006c49] border border-[#006c49]/30 hover:bg-[#6cf8bb]/40'
                        : isLocked
                        ? 'bg-[#f0f0f5] text-[#a0a0b0] opacity-60 cursor-not-allowed'
                        : 'bg-[#f8f9ff] text-[#0b1c30] border border-[#e5eeff] hover:border-[#0f2a90]'
                    }`}
                  >
                    <div>
                      <div className="font-mono text-[11px] font-bold tracking-wide">
                        {item.module_id}
                      </div>
                      <div className="text-xs line-clamp-1 opacity-90">
                        {item.title}
                      </div>
                    </div>

                    <div>
                      {isCompleted ? (
                        <span className="material-symbols-outlined text-sm text-[#006c49]" style={{ fontVariationSettings: "'FILL' 1" }}>
                          check_circle
                        </span>
                      ) : isLocked ? (
                        <span className="material-symbols-outlined text-sm text-[#a0a0b0]">
                          lock
                        </span>
                      ) : isCurrent ? (
                        <span className="material-symbols-outlined text-sm text-white animate-pulse">
                          edit_note
                        </span>
                      ) : (
                        <span className="material-symbols-outlined text-sm text-[#0f2a90]">
                          arrow_forward
                        </span>
                      )}
                    </div>
                  </button>
                );
              })
            ) : (
              <div className="text-center py-4 text-xs text-[#757684]">Đang tải danh sách bài...</div>
            )}
          </div>

          {/* Quick Actions at Sidebar Bottom */}
          <div className="pt-3 border-t border-[#e5eeff] space-y-2">
            <button
              onClick={() => setSetupModalOpen(true)}
              className="w-full py-2.5 px-3 bg-[#eff4ff] text-[#0f2a90] font-label-caps text-xs font-semibold rounded-xl hover:bg-[#dce9ff] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span className="material-symbols-outlined text-sm">tune</span>
              Cấu hình câu hỏi
            </button>
            <button
              onClick={onBackToPath}
              className="w-full py-2.5 px-3 border border-[#c5c5d4] text-[#454652] font-label-caps text-xs font-semibold rounded-xl hover:bg-[#eff4ff] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <span className="material-symbols-outlined text-sm">map</span>
              Về Bản đồ Học tập
            </button>
          </div>
        </aside>

        {/* RIGHT QUIZ CONTENT AREA */}
        <main className="flex-1 max-w-4xl mx-auto p-6 md:p-8 space-y-8">
          {forbiddenMsg && (
            <div className="p-5 bg-[#ffdad6] text-[#93000a] rounded-2xl border-2 border-[#ba1a1a] shadow-md font-mono text-sm">
              <h3 className="font-bold text-base mb-1">🚫 HTTP 403 FORBIDDEN - SEQUENTIAL GATING</h3>
              <p>{forbiddenMsg}</p>
              <button
                onClick={onBackToPath}
                className="mt-4 bg-[#ba1a1a] text-white px-5 py-2 rounded-full font-label-caps text-xs hover:bg-[#93000a] transition-all cursor-pointer"
              >
                Quay lại hoàn thành bài học trước
              </button>
            </div>
          )}

          {/* CONDITION: SUBMITTED -> DEDICATED RESULTS PAGE */}
          {submitted ? (
            <div className="space-y-8 animate-fadeIn">
              {/* Header Scoreboard Card */}
              <div className="bg-white rounded-3xl p-8 border-2 border-[#006c49] shadow-lg text-center relative overflow-hidden">
                <span className="font-label-caps text-xs text-[#006c49] bg-[#6cf8bb]/30 px-4 py-1.5 rounded-full font-bold uppercase tracking-wider">
                  KẾT QUẢ BÀI LÀM & CHẤM ĐIỂM CHI TIẾT
                </span>
                <h1 className="font-display-lg text-4xl md:text-5xl font-bold text-[#0b1c30] mt-4 mb-2">
                  {gradingResult?.total_score ?? 10.0} / {gradingResult?.max_score ?? 10.0} ĐIỂM
                </h1>
                <p className="font-mono text-sm font-bold text-[#006c49] mb-4">
                  Tỷ lệ chính xác: {gradingResult?.percentage ?? 100}% —{' '}
                  {gradingResult?.percentage >= 60
                    ? '🎉 ĐÃ HOÀN THÀNH (ĐÃ MỞ KHÓA BUỔI TIẾP THEO)'
                    : '🌱 CẦN LUYỆN TẬP THÊM'}
                </p>
                <p className="font-body-md text-xs text-[#454652] max-w-lg mx-auto bg-[#f8f9ff] p-3 rounded-2xl border border-[#c5c5d4]/40">
                  {gradingResult?.summary_recommendation ||
                    'Bài làm đã được chấm điểm tự động. Kết quả và các lỗ hổng kiến thức đã được lưu vào Hồ sơ Năng lực (StudentProgressAnalytics DB).'}
                </p>
              </div>

              {/* List of Question Results with AI Explanations */}
              <div className="space-y-6">
                <h2 className="font-headline-md text-xl font-bold text-[#0b1c30]">
                  Chi tiết từng câu hỏi & Giải thích từ AI Tutor:
                </h2>

                {currentQuestions.map((q: any, idx: number) => {
                  const qId = q.id || `Q${idx + 1}`;
                  const userAns = answers[qId] || 'Bỏ trống';
                  const correctAns = q.correct_answer || q.correctAnswer || 'A';
                  const qResult = gradingResult?.question_results?.find(
                    (r: any) => r.question_id === qId
                  );
                  const isCorrect = qResult
                    ? qResult.score > 0
                    : userAns.toLowerCase() === correctAns.toLowerCase();
                  const explanationText =
                    q.explanation ||
                    qResult?.feedback ||
                    'Giải thích dựa trên tài liệu bài giảng nguyên bản.';
                  const citationText = q.citation || qResult?.citation || '';

                  return (
                    <div
                      key={qId}
                      className={`bg-white rounded-3xl p-6 md:p-8 border-2 shadow-sm ${
                        isCorrect
                          ? 'border-[#006c49]/40 bg-[#f4fbf7]'
                          : 'border-[#ba1a1a]/40 bg-[#fff8f7]'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <span className="font-mono text-xs font-bold text-[#0f2a90]">
                          CÂU {idx + 1} / {currentQuestions.length} ({q.type || 'TRẮC NGHIỆM'})
                        </span>
                        <span
                          className={`font-mono text-xs px-3 py-1 rounded-full font-bold ${
                            isCorrect
                              ? 'bg-[#6cf8bb]/40 text-[#006c49]'
                              : 'bg-[#ffdad6] text-[#93000a]'
                          }`}
                        >
                          {isCorrect ? '✓ ĐÚNG (+1.0 ĐIỂM)' : '✗ CHƯA ĐÚNG (0 ĐIỂM)'}
                        </span>
                      </div>

                      <h3 className="font-headline-md text-base font-bold text-[#0b1c30] mb-4">
                        {q.question_text || q.question}
                      </h3>

                      {/* User Choice vs Correct Choice */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 text-xs font-mono">
                        <div className="p-3 rounded-2xl bg-white border border-[#c5c5d4]">
                          <span className="text-[#757684] block mb-1 font-sans">Câu trả lời của bạn:</span>
                          <span className={isCorrect ? 'text-[#006c49] font-bold' : 'text-[#ba1a1a] font-bold'}>
                            {userAns}
                          </span>
                        </div>
                        <div className="p-3 rounded-2xl bg-[#eff4ff] border border-[#0f2a90]/30">
                          <span className="text-[#0f2a90] block mb-1 font-sans">Đáp án chính xác:</span>
                          <span className="text-[#0f2a90] font-bold">{correctAns}</span>
                        </div>
                      </div>

                      {/* AI Detailed Explanation Box */}
                      <div className="p-4 bg-white rounded-2xl border-l-4 border-[#0f2a90] shadow-sm">
                        <div className="flex items-center gap-2 mb-1 text-xs font-bold text-[#0f2a90] font-mono">
                          <span className="material-symbols-outlined text-sm">lightbulb</span>
                          GIẢI THÍCH CHI TIẾT TỪ AI TUTOR:
                        </div>
                        <p className="font-body-md text-xs text-[#0b1c30] leading-relaxed mb-2">
                          {explanationText}
                        </p>
                        {citationText && (
                          <div className="font-mono text-[11px] text-[#0f2a90] bg-[#2e44a7]/10 px-2.5 py-1 rounded-md inline-block">
                            Trích dẫn bài giảng: {citationText}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Action Button */}
              <div className="text-center pt-4">
                <button
                  onClick={onBackToPath}
                  className="bg-[#0f2a90] text-white px-8 py-3.5 rounded-full font-label-caps text-xs font-bold shadow-md hover:bg-[#2e44a7] transition-all cursor-pointer"
                >
                  Quay lại Bản đồ Bài học để sang Buổi tiếp theo
                </button>
              </div>
            </div>
          ) : (
            /* CONDITION: UN-SUBMITTED -> DOING QUIZ QUESTIONS */
            currentQuestions.length === 0 ? (
              <div className="bg-white rounded-3xl p-10 border border-[#c5c5d4] shadow-sm text-center space-y-4">
                <span className="material-symbols-outlined text-5xl text-[#0f2a90]">quiz</span>
                <h3 className="font-headline-md text-xl font-bold text-[#0b1c30]">
                  Chưa có câu hỏi cho buổi học này ({quizId})
                </h3>
                <p className="font-body-md text-xs text-[#757684] max-w-md mx-auto">
                  Hãy bấm nút dưới đây để cấu hình số lượng câu hỏi và độ khó mong muốn. AI sẽ sinh đề bài thời gian thực dành riêng cho bạn!
                </p>
                <button
                  onClick={() => setSetupModalOpen(true)}
                  className="bg-[#0f2a90] text-white px-8 py-3.5 rounded-full font-label-caps text-xs font-bold shadow-md hover:bg-[#2e44a7] transition-all cursor-pointer inline-flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-base">auto_awesome</span>
                  Bấm để Sinh Đề Bài AI Ngay
                </button>
              </div>
            ) : (
              <div className="space-y-6">
              {currentQuestions.map((q: any, idx: number) => {
                const qId = q.id || `Q${idx + 1}`;
                return (
                  <div key={qId} className="bg-white rounded-3xl p-6 md:p-8 border border-[#c5c5d4] shadow-sm">
                    <div className="flex justify-between items-center mb-3 font-mono text-xs text-[#757684]">
                      <span className="font-bold text-[#0f2a90]">
                        CÂU {idx + 1} / {currentQuestions.length} ({q.type === 'multiple_choice' ? 'TRẮC NGHIỆM' : (q.type === 'fill_in_blank' ? 'ĐIỀN TỪ' : 'TỰ LUẬN NGẮN')})
                      </span>
                      <span>{q.citation || `[${quizId}]`}</span>
                    </div>

                    <h3 className="font-headline-md text-base md:text-lg font-bold text-[#0b1c30] mb-5">
                      {q.question_text || q.question}
                    </h3>

                    {/* Multiple Choice Options */}
                    {q.type === 'multiple_choice' && q.options && (
                      <div className="space-y-3">
                        {q.options.map((opt: string) => {
                          const isSelected = answers[qId] === opt;
                          return (
                            <label
                              key={opt}
                              onClick={() => handleSelectAnswer(qId, opt)}
                              className={`flex items-center p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                                isSelected
                                  ? 'border-[#0f2a90] bg-[#eff4ff] shadow-sm'
                                  : 'border-[#c5c5d4]/60 hover:border-[#0f2a90]/50 bg-white'
                              }`}
                            >
                              <div
                                className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                                  isSelected ? 'border-[#0f2a90] bg-[#0f2a90]' : 'border-[#c5c5d4]'
                                }`}
                              >
                                {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                              </div>
                              <span className="font-body-md text-xs text-[#0b1c30]">{opt}</span>
                            </label>
                          );
                        })}
                      </div>
                    )}

                    {/* Fill in blank Input */}
                    {q.type === 'fill_in_blank' && (
                      <div>
                        <input
                          type="text"
                          value={answers[qId] || ''}
                          onChange={(e) => handleSelectAnswer(qId, e.target.value)}
                          placeholder="Nhập từ hoặc cụm từ chính xác vào đây..."
                          className="w-full p-3.5 border-2 border-[#c5c5d4] rounded-2xl text-xs font-mono focus:border-[#0f2a90] outline-none"
                        />
                      </div>
                    )}

                    {/* Short Essay Textarea */}
                    {q.type === 'short_essay' && (
                      <div>
                        <textarea
                          rows={4}
                          value={answers[qId] || ''}
                          onChange={(e) => handleSelectAnswer(qId, e.target.value)}
                          placeholder="Viết câu trả lời tự luận ngắn (2-3 câu)..."
                          className="w-full p-4 border-2 border-[#c5c5d4] rounded-2xl text-xs font-mono focus:border-[#0f2a90] outline-none"
                        />
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Submit Quiz Action Bar */}
              <div className="pt-6 flex justify-end">
                <button
                  onClick={handleSubmitQuiz}
                  disabled={isSubmitting}
                  className="bg-[#0f2a90] text-white px-10 py-4 rounded-full font-label-caps text-xs font-bold shadow-lg hover:bg-[#2e44a7] transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <span className="material-symbols-outlined text-sm animate-spin">refresh</span>
                      Đang chấm điểm...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-sm">send</span>
                      Nộp bài làm & Xem giải thích AI
                    </>
                  )}
                </button>
              </div>
            </div>
            )
          )}
        </main>
      </div>

      {/* Setup Modal */}
      <QuizSetupModal
        isOpen={setupModalOpen}
        onClose={() => setSetupModalOpen(false)}
        onApplySetup={handleApplySetup}
      />
    </div>
  );
};
