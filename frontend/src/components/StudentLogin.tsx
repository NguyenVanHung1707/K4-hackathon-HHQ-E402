import React, { useState } from 'react';
import { StudentProfile } from '../types';

interface StudentLoginProps {
  onLogin: (profile: StudentProfile) => void;
  onBackToRoleSelect?: () => void;
}

export const StudentLogin: React.FC<StudentLoginProps> = ({ onLogin, onBackToRoleSelect }) => {
  const [fullName, setFullName] = useState('Nguyen Van A');
  const [studentId, setStudentId] = useState('2012345');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !studentId.trim()) return;

    try {
      await fetch('/api/student/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullName, studentId }),
      });
    } catch {
      // proceed if offline
    }

    onLogin({ fullName, studentId });
  };

  return (
    <div className="min-h-screen bg-[#f8f9ff] flex items-center justify-center p-4 antialiased text-[#0b1c30] relative overflow-hidden">
      {/* Background radial effects */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-[#dce9ff] rounded-full blur-3xl opacity-60 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-[#eff4ff] rounded-full blur-3xl opacity-60 pointer-events-none" />

      {onBackToRoleSelect && (
        <button
          onClick={onBackToRoleSelect}
          className="absolute top-6 left-6 flex items-center gap-2 text-[#454652] hover:text-[#0f2a90] font-label-caps text-xs transition-colors"
        >
          <span className="material-symbols-outlined text-sm">arrow_back</span>
          Đổi vai trò
        </button>
      )}

      <main className="w-full max-w-md relative z-10">
        <div className="bg-white rounded-2xl shadow-[0_4px_12px_rgba(0,0,0,0.03)] border border-[#e5eeff] overflow-hidden">
          <div className="p-8 md:p-10 flex flex-col items-center">
            {/* Logo Area */}
            <div className="mb-8 flex flex-col items-center">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAUvfo_dixjB29xDYG90IjH5Rl4GTSUJROotHNVCgfroFZk3j51WmuGyNhAi5IcESOcAhB7JD6b0n4ha2QV-N7SzyqozWcgyF67TCQ08T_tqby0mDi55r_LvYw2xoBvzseatmKFDA9DOvayOtS09MZalWyak2_wRATwbKbUBz7zfAN3NnY5p8Omu6IMsZGQciLuDOv77Qrq9686fG4TFyL3gx4t1mh6JEIzyT762-eKESLvsJzJS-RNRQ"
                alt="VLearn Logo"
                className="h-20 w-auto mb-4 object-contain"
              />
              <h1 className="font-headline-md text-2xl font-bold text-[#0f2a90] text-center">
                Welcome to VLearn
              </h1>
              <p className="font-body-md text-[#454652] text-center mt-2">
                Ready to start learning?
              </p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="w-full space-y-6">
              {/* Field 1: Họ và Tên */}
              <div className="bg-[#f8f9ff] rounded-[12px] p-1 border-2 border-transparent focus-within:border-[#0f2a90] transition-all">
                <div className="px-3 pt-2 pb-1 relative">
                  <label className="block font-label-caps text-xs text-[#454652] uppercase tracking-wider mb-1" htmlFor="fullName">
                    Họ và Tên
                  </label>
                  <div className="flex items-center">
                    <span className="material-symbols-outlined text-[#c5c5d4] mr-2" style={{ fontVariationSettings: "'FILL' 0" }}>
                      person
                    </span>
                    <input
                      id="fullName"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Nguyen Van A"
                      required
                      className="w-full bg-transparent border-none p-0 focus:ring-0 font-body-lg text-[#0b1c30] placeholder-[#c5c5d4] outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Field 2: MSSV */}
              <div className="bg-[#f8f9ff] rounded-[12px] p-1 border-2 border-transparent focus-within:border-[#0f2a90] transition-all">
                <div className="px-3 pt-2 pb-1 relative">
                  <label className="block font-label-caps text-xs text-[#454652] uppercase tracking-wider mb-1" htmlFor="studentId">
                    Mã số sinh viên (MSSV)
                  </label>
                  <div className="flex items-center">
                    <span className="material-symbols-outlined text-[#c5c5d4] mr-2" style={{ fontVariationSettings: "'FILL' 0" }}>
                      badge
                    </span>
                    <input
                      id="studentId"
                      type="text"
                      value={studentId}
                      onChange={(e) => setStudentId(e.target.value)}
                      placeholder="2012345"
                      required
                      className="w-full bg-transparent border-none p-0 focus:ring-0 font-body-lg text-[#0b1c30] placeholder-[#c5c5d4] outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="pt-4">
                <button
                  type="submit"
                  className="w-full relative group overflow-hidden rounded-full bg-[#006c49] text-white py-4 px-6 shadow-[0_4px_12px_rgba(0,108,73,0.2)] hover:shadow-[0_8px_24px_rgba(0,108,73,0.3)] transition-all duration-300 transform hover:-translate-y-1 active:translate-y-0 border-b-2 border-[#4edea3]/50 cursor-pointer"
                >
                  <div className="relative flex items-center justify-center space-x-2">
                    <span className="font-student-card-title text-lg font-bold">Vào lớp học</span>
                    <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform duration-300" style={{ fontVariationSettings: "'FILL' 1" }}>
                      arrow_forward
                    </span>
                  </div>
                </button>
              </div>
            </form>
          </div>

          {/* Bottom gradient bar */}
          <div className="h-2 w-full bg-gradient-to-r from-[#0f2a90] to-[#006c49]" />
        </div>
      </main>
    </div>
  );
};
