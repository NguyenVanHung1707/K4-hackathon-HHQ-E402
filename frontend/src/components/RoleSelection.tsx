import React from 'react';
import { ActiveScreen } from '../types';

interface RoleSelectionProps {
  onSelectRole: (role: 'teacher' | 'student', nextScreen?: ActiveScreen) => void;
}

export const RoleSelection: React.FC<RoleSelectionProps> = ({ onSelectRole }) => {
  return (
    <div className="bg-[#f8f9ff] text-[#0b1c30] min-h-screen flex items-center justify-center font-body-md relative overflow-hidden bg-pattern px-4 py-12">
      {/* Decorative ambient blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[#2e44a7]/20 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-[#6cf8bb]/20 blur-[100px] pointer-events-none" />

      <main className="w-full max-w-4xl px-4 md:px-10 py-8 relative z-10 flex flex-col items-center">
        {/* Logo Header */}
        <div className="text-center mb-12 flex flex-col items-center">
          <img
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAUvfo_dixjB29xDYG90IjH5Rl4GTSUJROotHNVCgfroFZk3j51WmuGyNhAi5IcESOcAhB7JD6b0n4ha2QV-N7SzyqozWcgyF67TCQ08T_tqby0mDi55r_LvYw2xoBvzseatmKFDA9DOvayOtS09MZalWyak2_wRATwbKbUBz7zfAN3NnY5p8Omu6IMsZGQciLuDOv77Qrq9686fG4TFyL3gx4t1mh6JEIzyT762-eKESLvsJzJS-RNRQ"
            alt="VLearn Logo"
            className="h-24 mb-6 object-contain"
          />
          <h1 className="font-display-lg text-3xl md:text-5xl text-[#0f2a90] text-center max-w-2xl mx-auto leading-tight font-bold">
            Chào mừng bạn đến với hệ thống học tập thông minh. Bạn là ai?
          </h1>
        </div>

        {/* Role Selection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-3xl">
          {/* Teacher Card */}
          <button
            onClick={() => onSelectRole('teacher', 'teacher-dashboard')}
            className="role-card group bg-white border-2 border-[#c5c5d4] rounded-2xl p-8 flex flex-col items-center text-center cursor-pointer outline-none focus:ring-4 focus:ring-[#2e44a7] relative overflow-hidden text-left"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-[#2e44a7]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="w-20 h-20 bg-[#2e44a7] rounded-full flex items-center justify-center mb-6 text-[#afbbff] group-hover:scale-110 transition-transform duration-300">
              <span className="material-symbols-outlined text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                person_apron
              </span>
            </div>
            <h2 className="font-headline-md text-2xl font-semibold text-[#0f2a90] mb-3">Giáo viên</h2>
            <p className="font-body-md text-[#454652] max-w-[250px] text-center">
              Quản lý lớp học và tạo nội dung AI
            </p>
            <div className="mt-8 px-6 py-2 rounded-full border border-[#0f2a90]/20 text-[#0f2a90] font-label-caps text-xs group-hover:bg-[#0f2a90] group-hover:text-white transition-colors duration-300">
              Chọn vai trò
            </div>
          </button>

          {/* Student Card */}
          <button
            onClick={() => onSelectRole('student', 'student-login')}
            className="role-card group bg-white border-2 border-[#c5c5d4] rounded-2xl p-8 flex flex-col items-center text-center cursor-pointer outline-none focus:ring-4 focus:ring-[#6cf8bb] relative overflow-hidden text-left"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-[#6cf8bb]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <div className="w-20 h-20 bg-[#6cf8bb] rounded-full flex items-center justify-center mb-6 text-[#00714d] group-hover:scale-110 transition-transform duration-300">
              <span className="material-symbols-outlined text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>
                school
              </span>
            </div>
            <h2 className="font-headline-md text-2xl font-semibold text-[#006c49] mb-3">Sinh viên</h2>
            <p className="font-body-md text-[#454652] max-w-[250px] text-center">
              Tham gia bài học và tương tác với AI Tutor
            </p>
            <div className="mt-8 px-6 py-2 rounded-full border border-[#006c49]/20 text-[#006c49] font-label-caps text-xs group-hover:bg-[#006c49] group-hover:text-white transition-colors duration-300">
              Chọn vai trò
            </div>
          </button>
        </div>
      </main>
    </div>
  );
};
