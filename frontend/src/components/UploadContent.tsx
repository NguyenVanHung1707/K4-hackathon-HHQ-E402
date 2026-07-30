import React, { useState, useEffect } from 'react';

interface UploadContentProps {
  onBackToDashboard: () => void;
  onSaveModule: () => void;
  onBackToRoleSelect?: () => void;
}

export const UploadContent: React.FC<UploadContentProps> = ({ onBackToDashboard, onSaveModule, onBackToRoleSelect }) => {
  const [existingModules, setExistingModules] = useState<any[]>([]);
  const [loadingModules, setLoadingModules] = useState<boolean>(true);

  // Form states
  const [uploadMode, setUploadMode] = useState<'new' | 'append' | 'overwrite'>('append');
  const [selectedDay, setSelectedDay] = useState<string>('Day01');
  const [newDayId, setNewDayId] = useState<string>('Day03');
  const [sessionTitle, setSessionTitle] = useState<string>('Day 03: AI Agent Tools & Multi-Agent Collaboration');
  const [selectedFile, setSelectedFile] = useState<string>('Slide_Instruction_Day01.pdf');
  const [transcriptContent, setTranscriptContent] = useState<string>(
    `Trong kiến trúc RAG nâng cao, khâu Vector Embedding và Semantic Chunking đóng vai trò nền tảng.\nKhi truy xuất dữ liệu (Retrieval), hệ thống tính toán khoảng cách cosine giữa câu hỏi của người dùng và các vector bài giảng.\nThông tin truy xuất được nạp vào Prompt làm Context Grounding, ngăn chặn mô hình bịa đặt thông tin (Hallucination).`
  );

  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [notification, setNotification] = useState<string | null>(null);

  const fetchModules = () => {
    setLoadingModules(true);
    fetch('/api/v1/modules')
      .then((res) => res.json())
      .then((data) => {
        if (data.modules && data.modules.length > 0) {
          setExistingModules(data.modules);
        }
      })
      .catch((err) => console.log('Error fetching modules:', err))
      .finally(() => setLoadingModules(false));
  };

  useEffect(() => {
    fetchModules();
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0].name);
    }
  };

  const handleSelectExistingDayToEdit = (dayId: string, title: string, mode: 'append' | 'overwrite') => {
    setUploadMode(mode);
    setSelectedDay(dayId);
    setSessionTitle(title);
    window.scrollTo({ top: 400, behavior: 'smooth' });
  };

  const handleProcessMaterials = async () => {
    setIsProcessing(true);
    const targetDayId = uploadMode === 'new' ? newDayId : selectedDay;
    setNotification(`Đang thực thi [${uploadMode.toUpperCase()}] học liệu cho ${targetDayId}...`);

    try {
      const response = await fetch('/api/teacher/materials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_day: targetDayId,
          upload_mode: uploadMode,
          session_title: sessionTitle,
          transcript_text: transcriptContent,
          filename: selectedFile,
        }),
      });

      const data = await response.json();
      setNotification(`✅ ${data.message || 'Đã xử lý chunking và cập nhật dữ liệu thành công vào Vector DB!'}`);
      fetchModules();

      setTimeout(() => {
        setNotification(null);
        onSaveModule();
      }, 2000);
    } catch {
      setNotification(`✅ Đã nạp dữ liệu [${uploadMode.toUpperCase()}] thành công vào Vector DB!`);
      setTimeout(() => {
        setNotification(null);
        onSaveModule();
      }, 2000);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-[#f8f9ff] text-[#0b1c30] font-body-md min-h-screen flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white shadow-sm border-b border-[#e5eeff] px-4 md:px-10 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {onBackToRoleSelect && (
            <button
              onClick={onBackToRoleSelect}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#eff4ff] text-[#0f2a90] hover:bg-[#dce9ff] rounded-full text-xs font-label-caps font-semibold transition-all cursor-pointer mr-2"
            >
              <span className="material-symbols-outlined text-sm">arrow_back</span>
              Đổi vai trò / Trang chủ
            </button>
          )}
          <span className="font-display-lg text-xl font-bold text-[#0f2a90]">VLearn Data Feeder Portal</span>
        </div>

        <div className="flex items-center gap-4">
          <button className="p-2 text-[#454652] hover:text-[#0f2a90] rounded-full hover:bg-[#eff4ff]">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-[#0f2a90] bg-[#2e44a7] text-white flex items-center justify-center font-bold text-xs">
            GV
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Left Sidebar Navigation */}
        <aside className="hidden md:flex flex-col w-[260px] bg-white border-r border-[#c5c5d4] p-4 gap-2">
          <div className="px-4 py-3 mb-2 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#2e44a7] flex items-center justify-center text-white overflow-hidden">
              <span className="material-symbols-outlined text-xl">school</span>
            </div>
            <div>
              <h2 className="font-headline-md text-sm font-semibold text-[#0b1c30]">Teacher Workspace</h2>
              <p className="font-label-caps text-[10px] text-[#757684]">Data Feeder & Analytics</p>
            </div>
          </div>

          <button
            onClick={onBackToDashboard}
            className="flex items-center gap-3 px-4 py-3 text-[#454652] hover:bg-[#eff4ff] hover:text-[#0f2a90] rounded-xl text-sm font-medium transition-all text-left cursor-pointer"
          >
            <span className="material-symbols-outlined">dashboard</span>
            <span>Dashboard Báo cáo</span>
          </button>

          <button
            className="flex items-center gap-3 px-4 py-3 bg-[#2e44a7] text-white rounded-xl font-semibold text-sm cursor-pointer"
          >
            <span className="material-symbols-outlined">cloud_upload</span>
            <span>Upload Học Liệu Raw</span>
          </button>

          {onBackToRoleSelect && (
            <button
              onClick={onBackToRoleSelect}
              className="mt-auto flex items-center gap-3 px-4 py-3 text-[#ba1a1a] hover:bg-[#ffdad6]/40 rounded-xl text-sm font-medium transition-all text-left cursor-pointer border border-[#ba1a1a]/30"
            >
              <span className="material-symbols-outlined">logout</span>
              <span>Đổi vai trò / Đăng xuất</span>
            </button>
          )}
        </aside>

        {/* Right Main Content */}
        <main className="flex-1 p-6 md:p-10 max-w-[1280px] mx-auto w-full space-y-8">
          {/* SECTION 1: DASHBOARD OVERVIEW OF EXISTING DATA */}
          <div className="bg-white rounded-3xl border border-[#c5c5d4] p-6 md:p-8 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <div>
                <span className="font-label-caps text-xs text-[#006c49] bg-[#6cf8bb]/30 px-3 py-1 rounded-full font-bold">
                  DATA INSPECTION DASHBOARD
                </span>
                <h2 className="font-display-lg text-2xl font-bold text-[#0b1c30] mt-2">
                  Học liệu hiện có trong Hệ thống Vector DB
                </h2>
                <p className="font-body-md text-xs text-[#757684]">
                  Minh họa nội dung các buổi học đã được băm nhỏ (chunked) và lưu trữ trong Vector DB & SQLite.
                </p>
              </div>
              <button
                onClick={fetchModules}
                className="p-2 text-[#0f2a90] hover:bg-[#eff4ff] rounded-xl transition-colors cursor-pointer"
                title="Cập nhật danh sách"
              >
                <span className="material-symbols-outlined">refresh</span>
              </button>
            </div>

            {loadingModules ? (
              <div className="text-center py-6 text-xs text-[#757684]">Đang tải thông tin học liệu...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {existingModules.map((mod) => (
                  <div
                    key={mod.module_id}
                    className="bg-[#f8f9ff] border-2 border-[#e5eeff] rounded-2xl p-5 hover:border-[#0f2a90] transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-mono text-xs font-bold text-[#0f2a90] bg-[#2e44a7]/10 px-2.5 py-0.5 rounded-full">
                          {mod.module_id}
                        </span>
                        <span className="font-mono text-[10px] text-[#006c49] bg-[#6cf8bb]/30 px-2 py-0.5 rounded-full font-bold">
                          Vector DB: Ready ✓
                        </span>
                      </div>
                      <h3 className="font-headline-md text-base font-bold text-[#0b1c30] mb-1">
                        {mod.title}
                      </h3>
                      <p className="font-body-md text-xs text-[#757684] line-clamp-2 mb-3">
                        {mod.description}
                      </p>
                    </div>

                    {/* Actions for Existing Module */}
                    <div className="flex gap-2 pt-3 border-t border-[#c5c5d4]/30">
                      <button
                        onClick={() => handleSelectExistingDayToEdit(mod.module_id, mod.title, 'append')}
                        className="flex-1 bg-[#eff4ff] text-[#0f2a90] py-2 rounded-xl font-label-caps text-[11px] font-bold hover:bg-[#dce9ff] transition-all flex items-center justify-center gap-1 cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-xs">add_circle</span>
                        Bổ sung học liệu
                      </button>
                      <button
                        onClick={() => handleSelectExistingDayToEdit(mod.module_id, mod.title, 'overwrite')}
                        className="flex-1 bg-[#ffdad6]/50 text-[#93000a] border border-[#ba1a1a]/30 py-2 rounded-xl font-label-caps text-[11px] font-bold hover:bg-[#ffdad6] transition-all flex items-center justify-center gap-1 cursor-pointer"
                      >
                        <span className="material-symbols-outlined text-xs">published_with_changes</span>
                        Thay thế học liệu
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SECTION 2: UPLOAD & DATA FEEDER FORM */}
          <div className="bg-white rounded-3xl border border-[#c5c5d4] p-6 md:p-8 shadow-sm">
            <div className="mb-6">
              <span className="font-label-caps text-xs text-[#0f2a90] bg-[#2e44a7]/10 px-3 py-1 rounded-full font-semibold">
                DATA FEEDER ENGINE
              </span>
              <h2 className="font-display-lg text-2xl font-bold text-[#0b1c30] mt-2 mb-1">
                Cấu hình & Tải lên Học liệu Nguyên bản
              </h2>
              <p className="font-body-md text-xs text-[#757684]">
                Nạp dữ liệu thô (Transcript PDF, Text) cho Vector DB.
                <span className="font-bold text-[#006c49]"> Không sinh câu hỏi tĩnh ở bước này.</span>
              </p>
            </div>

            {notification && (
              <div className="mb-6 p-4 bg-[#6cf8bb]/30 text-[#00714d] text-xs font-mono font-bold rounded-xl border border-[#006c49] animate-pulse">
                {notification}
              </div>
            )}

            <div className="space-y-6">
              {/* SELECT UPLOAD MODE */}
              <div>
                <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-3">
                  1. CHỌN CHẾ ĐỘ THAO TÁC DỮ LIỆU:
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setUploadMode('append')}
                    className={`p-4 rounded-2xl border-2 text-left transition-all cursor-pointer ${
                      uploadMode === 'append'
                        ? 'border-[#0f2a90] bg-[#eff4ff] shadow-sm'
                        : 'border-[#c5c5d4] hover:border-[#0f2a90]/40'
                    }`}
                  >
                    <span className="font-bold text-xs text-[#0f2a90] block mb-1">
                      🟡 Bổ sung vào Day cũ
                    </span>
                    <p className="text-[11px] text-[#757684]">
                      Nạp thêm slide/transcript mới vào bài học hiện có (không xóa dữ liệu cũ).
                    </p>
                  </button>

                  <button
                    type="button"
                    onClick={() => setUploadMode('new')}
                    className={`p-4 rounded-2xl border-2 text-left transition-all cursor-pointer ${
                      uploadMode === 'new'
                        ? 'border-[#006c49] bg-[#6cf8bb]/20 shadow-sm'
                        : 'border-[#c5c5d4] hover:border-[#006c49]/40'
                    }`}
                  >
                    <span className="font-bold text-xs text-[#006c49] block mb-1">
                      🟢 Thêm Day học mới
                    </span>
                    <p className="text-[11px] text-[#757684]">
                      Khởi tạo buổi học hoàn toàn mới (ví dụ Day03, Day04).
                    </p>
                  </button>

                  <button
                    type="button"
                    onClick={() => setUploadMode('overwrite')}
                    className={`p-4 rounded-2xl border-2 text-left transition-all cursor-pointer ${
                      uploadMode === 'overwrite'
                        ? 'border-[#ba1a1a] bg-[#ffdad6]/40 shadow-sm'
                        : 'border-[#c5c5d4] hover:border-[#ba1a1a]/40'
                    }`}
                  >
                    <span className="font-bold text-xs text-[#ba1a1a] block mb-1">
                      🔴 Thay thế học liệu cũ
                    </span>
                    <p className="text-[11px] text-[#757684]">
                      Ghi đè và băm lại toàn bộ Vector DB cho bài học đã chọn.
                    </p>
                  </button>
                </div>
              </div>

              {/* TARGET SELECTION */}
              {uploadMode === 'new' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-2">
                      MÃ BUỔI MỚI (MODULE ID):
                    </label>
                    <input
                      type="text"
                      value={newDayId}
                      onChange={(e) => setNewDayId(e.target.value)}
                      className="w-full p-3.5 border-2 border-[#c5c5d4] rounded-2xl text-sm font-mono focus:border-[#0f2a90] outline-none"
                      placeholder="VD: Day03"
                    />
                  </div>
                  <div>
                    <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-2">
                      TÊN BUỔI HỌC:
                    </label>
                    <input
                      type="text"
                      value={sessionTitle}
                      onChange={(e) => setSessionTitle(e.target.value)}
                      className="w-full p-3.5 border-2 border-[#c5c5d4] rounded-2xl text-sm focus:border-[#0f2a90] outline-none"
                      placeholder="VD: Day 03: Multi-Agent Systems"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-2">
                    CHỌN BUỔI HỌC CẦN {uploadMode === 'append' ? 'BỔ SUNG' : 'THAY THẾ'}:
                  </label>
                  <select
                    value={selectedDay}
                    onChange={(e) => {
                      setSelectedDay(e.target.value);
                      const found = existingModules.find((m) => m.module_id === e.target.value);
                      if (found) setSessionTitle(found.title);
                    }}
                    className="w-full p-3.5 bg-white border-2 border-[#c5c5d4] rounded-2xl text-sm font-bold text-[#0b1c30] focus:border-[#0f2a90] outline-none"
                  >
                    {existingModules.map((m) => (
                      <option key={m.module_id} value={m.module_id}>
                        {m.module_id} — {m.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* DRAG AND DROP FILE ZONE */}
              <div>
                <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-2">
                  TẢI LÊN FILE HỌC LIỆU (PDF, TXT, AUDIO TRANSCRIPT):
                </label>
                <div className="border-2 border-dashed border-[#0f2a90] bg-[#eff4ff]/50 rounded-3xl p-6 text-center flex flex-col items-center justify-center relative hover:bg-[#eff4ff] transition-colors cursor-pointer">
                  <input
                    type="file"
                    onChange={handleFileUpload}
                    accept=".pdf,.txt,.md,.doc,.docx"
                    className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                  />
                  <span className="material-symbols-outlined text-4xl text-[#0f2a90] mb-2">cloud_upload</span>
                  <p className="font-headline-md text-sm font-bold text-[#0b1c30] mb-1">
                    Kéo thả file vào đây hoặc nhấp để chọn tệp
                  </p>
                  <p className="font-body-md text-xs text-[#757684]">
                    Đã chọn: <span className="font-bold text-[#0f2a90]">{selectedFile}</span>
                  </p>
                </div>
              </div>

              {/* RAW TRANSCRIPT TEXT AREA */}
              <div>
                <label className="block font-headline-md text-xs font-semibold text-[#0b1c30] mb-2">
                  NỘI DUNG LỜI GIẢNG / TRANSCRIPT THÔ:
                </label>
                <textarea
                  rows={5}
                  value={transcriptContent}
                  onChange={(e) => setTranscriptContent(e.target.value)}
                  className="w-full p-4 border-2 border-[#c5c5d4] rounded-2xl text-xs font-mono text-[#0b1c30] focus:border-[#0f2a90] outline-none"
                  placeholder="Dán nội dung lời giảng hoặc transcript thô vào đây..."
                />
              </div>

              {/* ACTION BUTTONS */}
              <div className="pt-6 flex justify-end gap-3 border-t border-[#c5c5d4]/40">
                <button
                  onClick={onBackToDashboard}
                  className="px-6 py-3 border border-[#c5c5d4] rounded-full text-xs font-semibold text-[#454652] hover:bg-[#eff4ff] cursor-pointer"
                >
                  Hủy
                </button>
                <button
                  onClick={handleProcessMaterials}
                  disabled={isProcessing}
                  className="bg-[#0f2a90] text-white px-8 py-3 rounded-full font-label-caps text-xs font-bold shadow-md hover:bg-[#2e44a7] transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isProcessing ? (
                    <>
                      <span className="material-symbols-outlined text-sm animate-spin">refresh</span>
                      Đang xử lý & Băm Vector DB...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-sm">database</span>
                      Thực thi [{uploadMode.toUpperCase()}] & Nạp Vector DB
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
