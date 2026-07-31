import React, { useState, useEffect } from 'react';
import { StudentProfile } from '../types';
import { QuizSetupModal } from './QuizSetupModal';
import { LessonSummaryModal } from './LessonSummaryModal';

interface LearningPathProps {
  studentProfile: StudentProfile;
  onStartQuiz: (quizId?: string, quizData?: any) => void;
}

export const LearningPath: React.FC<LearningPathProps> = ({ studentProfile, onStartQuiz }) => {
  const [progressMap, setProgressMap] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [forbiddenError, setForbiddenError] = useState<string | null>(null);

  // Setup Modal State
  const [setupModalOpen, setSetupModalOpen] = useState<boolean>(false);
  const [selectedModule, setSelectedModule] = useState<{ id: string; title: string } | null>(null);
  const [summarySessionId, setSummarySessionId] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/student/progress?student_id=${studentProfile.studentId || '2012345'}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.progress && data.progress.length > 0) {
          setProgressMap(data.progress);
        }
      })
      .catch((err) => console.log('Error fetching student progress:', err))
      .finally(() => setLoading(false));
  }, [studentProfile]);

  const handleLessonClick = async (moduleItem: any) => {
    if (moduleItem.status === 'locked') {
      setForbiddenError(`403 Forbidden: Yêu cầu hoàn thành bài tập của buổi trước trước khi mở khóa ${moduleItem.title}!`);
      setTimeout(() => setForbiddenError(null), 5000);
      return;
    }

    // Check if student already has a generated quiz -> Enter directly!
    try {
      const res = await fetch(
        `/api/student/session/${moduleItem.module_id}/quiz?student_id=${studentProfile.studentId || '2012345'}`
      );
      const data = await res.json();

      if (data.has_existing && data.questions && data.questions.length > 0) {
        // Direct Entry: Vào thẳng bài làm đã tạo trước đó
        onStartQuiz(moduleItem.module_id, data);
        return;
      }
    } catch {
      // fallback
    }

    // First time -> Open Setup Modal
    setSelectedModule({ id: moduleItem.module_id, title: moduleItem.title });
    setSetupModalOpen(true);
  };

  const handleForceOpenSetup = (moduleItem: any, e: React.MouseEvent) => {
    e.stopPropagation();
    if (moduleItem.status === 'locked') return;
    setSelectedModule({ id: moduleItem.module_id, title: moduleItem.title });
    setSetupModalOpen(true);
  };

  const defaultItems = [
    {
      module_id: 'Day01',
      title: 'Buổi 1 (Day01)',
      session: 'Day 01: Nền tảng LLM, Transformer & Attention Mechanism',
      status: 'unlocked',
      weak_concepts: ['Transformer Attention', 'Token Embeddings'],
    },
    {
      module_id: 'Day02',
      title: 'Buổi 2 (Day02)',
      session: 'Day 02: Xác định bài toán cho AI & Problem Statement',
      status: 'locked',
      weak_concepts: [],
    },
  ];

  const displayMap = progressMap.length > 0 ? progressMap : defaultItems;

  return (
    <div className="bg-[#f8f9ff] text-[#0b1c30] min-h-screen font-body-md flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-[#e5eeff] px-4 md:px-10 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="font-display-lg text-2xl font-bold text-[#0f2a90]">VLearn</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="bg-white border border-[#c5c5d4] rounded-full px-4 py-1.5 flex items-center gap-4 shadow-sm text-xs font-label-caps">
            <div className="flex items-center gap-1.5 text-[#006c49]">
              <span className="material-symbols-outlined text-sm text-[#006c49]">grade</span>
              <span>XP: 1,250</span>
            </div>
            <div className="h-3 w-px bg-[#c5c5d4]" />
            <div className="flex items-center gap-1.5 text-[#6e4400]">
              <span
                className="material-symbols-outlined text-sm text-[#ffae3c]"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                local_fire_department
              </span>
              <span>5 DAY STREAK</span>
            </div>
          </div>

          <div className="w-8 h-8 rounded-full bg-[#2e44a7] text-white font-bold flex items-center justify-center text-xs border border-[#0f2a90]">
            {studentProfile.fullName.charAt(0) || 'S'}
          </div>
        </div>
      </header>

      {/* 403 Forbidden Banner */}
      {forbiddenError && (
        <div className="bg-[#ffdad6] text-[#93000a] p-4 text-center text-xs font-semibold font-mono border-b border-[#ba1a1a] shadow-sm animate-bounce">
          ⚠️ {forbiddenError}
        </div>
      )}

      {/* Main Path Canvas */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-10 flex flex-col items-center">
        <div className="text-center mb-12">
          <h1 className="font-display-lg text-4xl md:text-5xl font-bold text-[#0f2a90] mb-3">
            My Adaptive Learning Path
          </h1>
          <p className="font-body-lg text-[#454652] max-w-lg mx-auto">
            Học tập chủ động & thích ứng. Nhấp vào bài học unlocked để làm bài trực tiếp hoặc cài đặt tạo mới!
          </p>
        </div>

        {/* Path Map */}
        <div className="w-full max-w-md relative flex flex-col items-center gap-10 py-4">
          {loading ? (
            <div className="text-center py-8 text-[#454652]">Đang kiểm tra hồ sơ năng lực & tiến độ...</div>
          ) : (
            displayMap.map((item) => {
              const isCompleted = item.status === 'completed';
              const isUnlocked = item.status === 'unlocked' || item.status === 'in_progress';
              const isLocked = item.status === 'locked';

              return (
                <div key={item.module_id} className="relative z-10 flex flex-col items-center w-full">
                  <div className="flex items-center gap-6 w-full justify-center">
                    {/* Icon Ring */}
                    <div
                      className={`w-16 h-16 rounded-full border-4 ${
                        isCompleted
                          ? 'border-[#006c49] bg-[#006c49] text-white'
                          : isUnlocked
                          ? 'border-[#2e44a7] bg-[#0f2a90] text-white animate-pulse'
                          : 'bg-[#e5eeff] text-[#757684] border-[#c5c5d4] opacity-60'
                      } flex items-center justify-center shadow-lg relative`}
                    >
                      <span className="material-symbols-outlined text-3xl font-bold">
                        {isCompleted ? 'check' : isUnlocked ? 'play_arrow' : 'lock'}
                      </span>
                    </div>

                    {/* Lesson Card */}
                    <div
                      className={`bg-white border-2 ${
                        isLocked ? 'border-[#c5c5d4] opacity-60' : 'border-[#0f2a90]'
                      } rounded-2xl p-5 shadow-md w-72 text-left`}
                    >
                      <div className="flex justify-between items-start">
                        <p className="font-headline-md text-base font-semibold text-[#0f2a90] mb-1">
                          {item.title}
                        </p>
                        {isLocked && <span className="text-xs text-[#ba1a1a] font-mono font-bold">403 LOCKED</span>}
                      </div>

                      <p className="font-body-md text-xs text-[#454652] mb-1">
                        {item.session}
                      </p>

                      {item.weak_concepts?.length > 0 && (
                        <p className="font-mono text-[10px] text-[#ba1a1a] bg-[#ffdad6]/40 p-1.5 rounded mb-3">
                          📍 Ôn lại điểm yếu: {item.weak_concepts.join(', ')}
                        </p>
                      )}

                      {/* Main Action Buttons */}
                      <div className="space-y-2 mt-2">
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            setSummarySessionId(item.module_id);
                          }}
                          className="w-full bg-white text-[#0f2a90] border border-[#2e44a7]/40 py-2 rounded-lg font-label-caps text-[11px] font-semibold hover:bg-[#eff4ff] transition-all flex items-center justify-center gap-1 cursor-pointer"
                        >
                          <span className="material-symbols-outlined text-sm">summarize</span>
                          Xem tóm tắt bài học
                        </button>
                        <button
                          onClick={() => handleLessonClick(item)}
                          className={`w-full text-white py-2.5 rounded-full font-label-caps text-xs transition-all flex items-center justify-center gap-2 shadow cursor-pointer ${
                            isLocked ? 'bg-[#757684] hover:bg-[#454652]' : 'bg-[#0f2a90] hover:bg-[#2e44a7]'
                          }`}
                        >
                          {isCompleted
                            ? 'Làm lại bài tập (Vào trực tiếp)'
                            : isUnlocked
                            ? 'Vào làm bài trực tiếp'
                            : 'Khóa chặn (Locked 🔒)'}
                        </button>

                        {isUnlocked && (
                          <button
                            onClick={(e) => handleForceOpenSetup(item, e)}
                            className="w-full bg-[#eff4ff] text-[#0f2a90] border border-[#2e44a7]/40 py-2 rounded-full font-label-caps text-[11px] font-semibold hover:bg-[#dce9ff] transition-all flex items-center justify-center gap-1 cursor-pointer"
                          >
                            <span className="material-symbols-outlined text-xs">tune</span>
                            Tạo thêm / Cấu hình lại đề AI
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>

      <LessonSummaryModal
        isOpen={Boolean(summarySessionId)}
        sessionId={summarySessionId || ''}
        studentId={studentProfile.studentId || '2012345'}
        onClose={() => setSummarySessionId(null)}
      />

      {/* Quiz Setup Modal Component */}
      <QuizSetupModal
        isOpen={setupModalOpen}
        sessionTitle={selectedModule?.title || ''}
        sessionId={selectedModule?.id || ''}
        studentId={studentProfile.studentId || '2012345'}
        onClose={() => setSetupModalOpen(false)}
        onStartQuiz={(quizData) => {
          setSetupModalOpen(false);
          onStartQuiz(selectedModule?.id, quizData);
        }}
      />
    </div>
  );
};
