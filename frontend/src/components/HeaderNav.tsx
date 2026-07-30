import React from 'react';
import { ActiveScreen } from '../types';

interface HeaderNavProps {
  activeScreen: ActiveScreen;
  onNavigate: (screen: ActiveScreen) => void;
}

export const HeaderNav: React.FC<HeaderNavProps> = ({ activeScreen, onNavigate }) => {
  return (
    <div className="bg-[#0b1c30] text-white px-4 py-2 flex flex-wrap items-center justify-between gap-2 border-b border-[#213145] text-xs font-label-caps z-50 relative">
      <div className="flex items-center gap-2">
        <span className="material-symbols-outlined text-sm text-[#afbbff]">auto_awesome</span>
        <span className="font-bold text-[#afbbff]">VLearn Screen Switcher:</span>
      </div>

      <div className="flex flex-wrap items-center gap-1">
        <button
          onClick={() => onNavigate('role-select')}
          className={`px-3 py-1 rounded-full border transition-all cursor-pointer ${
            activeScreen === 'role-select'
              ? 'bg-[#2e44a7] text-white border-[#afbbff]'
              : 'border-[#454652] text-[#d3e4fe] hover:bg-[#213145]'
          }`}
        >
          1. Role Select
        </button>

        <button
          onClick={() => onNavigate('student-login')}
          className={`px-3 py-1 rounded-full border transition-all cursor-pointer ${
            activeScreen === 'student-login'
              ? 'bg-[#2e44a7] text-white border-[#afbbff]'
              : 'border-[#454652] text-[#d3e4fe] hover:bg-[#213145]'
          }`}
        >
          2. Student Login
        </button>

        <button
          onClick={() => onNavigate('learning-path')}
          className={`px-3 py-1 rounded-full border transition-all cursor-pointer ${
            activeScreen === 'learning-path'
              ? 'bg-[#2e44a7] text-white border-[#afbbff]'
              : 'border-[#454652] text-[#d3e4fe] hover:bg-[#213145]'
          }`}
        >
          3. Learning Path
        </button>

        <button
          onClick={() => onNavigate('quiz')}
          className={`px-3 py-1 rounded-full border transition-all cursor-pointer ${
            activeScreen === 'quiz'
              ? 'bg-[#2e44a7] text-white border-[#afbbff]'
              : 'border-[#454652] text-[#d3e4fe] hover:bg-[#213145]'
          }`}
        >
          4. Quiz & AI Tutor
        </button>

        <button
          onClick={() => onNavigate('teacher-dashboard')}
          className={`px-3 py-1 rounded-full border transition-all cursor-pointer ${
            activeScreen === 'teacher-dashboard'
              ? 'bg-[#2e44a7] text-white border-[#afbbff]'
              : 'border-[#454652] text-[#d3e4fe] hover:bg-[#213145]'
          }`}
        >
          5. Teacher Dashboard
        </button>

        <button
          onClick={() => onNavigate('teacher-upload')}
          className={`px-3 py-1 rounded-full border transition-all cursor-pointer ${
            activeScreen === 'teacher-upload'
              ? 'bg-[#2e44a7] text-white border-[#afbbff]'
              : 'border-[#454652] text-[#d3e4fe] hover:bg-[#213145]'
          }`}
        >
          6. AI Quiz Creator
        </button>
      </div>
    </div>
  );
};
