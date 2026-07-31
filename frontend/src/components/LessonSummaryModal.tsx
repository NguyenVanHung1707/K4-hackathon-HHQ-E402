import React, { useEffect, useState } from 'react';

interface LessonSummaryModalProps {
  isOpen: boolean;
  sessionId: string;
  studentId: string;
  onClose: () => void;
}

export const LessonSummaryModal: React.FC<LessonSummaryModalProps> = ({
  isOpen,
  sessionId,
  studentId,
  onClose,
}) => {
  const [summary, setSummary] = useState<any>(null);
  const [loadedSessionId, setLoadedSessionId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState<number>(0);

  useEffect(() => {
    if (!isOpen || !sessionId) return;
    if (summary && loadedSessionId === sessionId && retryKey === 0) return;

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetch(
      `/api/student/session/${sessionId}/summary?student_id=${studentId || '2012345'}`,
      { signal: controller.signal }
    )
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || 'Không thể tạo bản tóm tắt bài học.');
        }
        return data;
      })
      .then((data) => {
        setSummary(data.summary);
        setLoadedSessionId(sessionId);
        setRetryKey(0);
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError.message || 'Không thể tạo bản tóm tắt bài học.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [isOpen, sessionId, studentId, retryKey]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[70] bg-black/50 p-4 flex items-center justify-center">
      <div
        className="w-full max-w-3xl max-h-[88vh] overflow-hidden bg-white rounded-2xl shadow-2xl border border-[#c5c5d4] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-labelledby="lesson-summary-title"
      >
        <div className="px-5 md:px-7 py-4 border-b border-[#e5eeff] flex items-center justify-between gap-4">
          <div className="min-w-0">
            <p className="font-mono text-[11px] font-bold text-[#0f2a90]">{sessionId}</p>
            <h2 id="lesson-summary-title" className="text-lg font-bold text-[#0b1c30] truncate">
              {summary?.title || 'Tóm tắt bài học'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 shrink-0 rounded-full hover:bg-[#eff4ff] text-[#454652] flex items-center justify-center cursor-pointer"
            title="Đóng"
            aria-label="Đóng bản tóm tắt"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="overflow-y-auto px-5 md:px-7 py-5 md:py-6">
          {loading ? (
            <div className="min-h-56 flex flex-col items-center justify-center gap-3 text-[#0f2a90]">
              <span className="material-symbols-outlined text-3xl animate-spin">progress_activity</span>
              <p className="text-sm font-semibold">Đang tổng hợp nội dung bài học...</p>
            </div>
          ) : error ? (
            <div className="min-h-48 flex flex-col items-center justify-center text-center gap-3">
              <span className="material-symbols-outlined text-3xl text-[#ba1a1a]">error</span>
              <p className="text-sm text-[#93000a]">{error}</p>
              <button
                onClick={() => setRetryKey((value) => value + 1)}
                className="px-4 py-2 bg-[#0f2a90] text-white rounded-lg text-xs font-bold cursor-pointer"
              >
                Thử lại
              </button>
            </div>
          ) : summary ? (
            <div className="space-y-7">
              <section>
                <h3 className="text-sm font-bold text-[#0f2a90] mb-2">Tổng quan</h3>
                <p className="text-sm leading-7 text-[#30313d]">{summary.overview}</p>
              </section>

              {summary.key_points?.length > 0 && (
                <section>
                  <h3 className="text-sm font-bold text-[#0f2a90] mb-3">Ý chính cần nhớ</h3>
                  <ol className="space-y-4">
                    {summary.key_points.map((item: any, index: number) => (
                      <li key={`${item.citation}-${index}`} className="flex gap-3">
                        <span className="font-mono text-xs font-bold text-[#0f2a90] pt-0.5">
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        <div>
                          <p className="text-sm leading-6 text-[#30313d]">{item.text}</p>
                          <p className="mt-1 font-mono text-[10px] text-[#667085]">{item.citation}</p>
                        </div>
                      </li>
                    ))}
                  </ol>
                </section>
              )}

              {summary.concepts?.length > 0 && (
                <section>
                  <h3 className="text-sm font-bold text-[#0f2a90] mb-3">Khái niệm trọng tâm</h3>
                  <ul className="grid sm:grid-cols-2 gap-x-8 gap-y-2">
                    {summary.concepts.map((concept: string) => (
                      <li key={concept} className="text-sm text-[#30313d] flex gap-2">
                        <span className="text-[#006c49]">•</span>
                        {concept}
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {summary.practical_examples?.length > 0 && (
                <section>
                  <h3 className="text-sm font-bold text-[#0f2a90] mb-3">Ví dụ trong bài giảng</h3>
                  <div className="space-y-4">
                    {summary.practical_examples.map((item: any, index: number) => (
                      <div key={`${item.citation}-${index}`} className="border-l-2 border-[#006c49] pl-4">
                        <p className="text-sm leading-6 text-[#30313d]">{item.text}</p>
                        <p className="mt-1 font-mono text-[10px] text-[#667085]">{item.citation}</p>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};
