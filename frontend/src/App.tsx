/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { ActiveScreen, StudentProfile, UserRole } from './types';
import { RoleSelection } from './components/RoleSelection';
import { StudentLogin } from './components/StudentLogin';
import { LearningPath } from './components/LearningPath';
import { StudentQuiz } from './components/StudentQuiz';
import { TeacherDashboard } from './components/TeacherDashboard';
import { UploadContent } from './components/UploadContent';
import { HeaderNav } from './components/HeaderNav';

export default function App() {
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [activeScreen, setActiveScreen] = useState<ActiveScreen>('role-select');
  const [studentProfile, setStudentProfile] = useState<StudentProfile>({
    fullName: 'Nguyen Van A',
    studentId: '2012345',
  });

  const [activeQuizId, setActiveQuizId] = useState<string>('MOD-01');

  const handleSelectRole = (role: UserRole, nextScreen?: ActiveScreen) => {
    setUserRole(role);
    if (nextScreen) {
      setActiveScreen(nextScreen);
    } else if (role === 'teacher') {
      setActiveScreen('teacher-dashboard');
    } else if (role === 'student') {
      setActiveScreen('student-login');
    }
  };

  const handleStudentLogin = (profile: StudentProfile) => {
    setStudentProfile(profile);
    setUserRole('student');
    setActiveScreen('learning-path');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f8f9ff]">

      {/* Screen Views */}
      <div className="flex-1">
        {activeScreen === 'role-select' && (
          <RoleSelection onSelectRole={handleSelectRole} />
        )}

        {activeScreen === 'student-login' && (
          <StudentLogin
            onLogin={handleStudentLogin}
            onBackToRoleSelect={() => setActiveScreen('role-select')}
          />
        )}

        {activeScreen === 'learning-path' && (
          <LearningPath
            studentProfile={studentProfile}
            onStartQuiz={(quizId) => {
              if (quizId) setActiveQuizId(quizId);
              setActiveScreen('quiz');
            }}
          />
        )}

        {activeScreen === 'quiz' && (
          <StudentQuiz
            quizId={activeQuizId}
            studentProfile={studentProfile}
            onBackToPath={() => setActiveScreen('learning-path')}
            onSelectSession={(sessionId) => setActiveQuizId(sessionId)}
          />
        )}

        {activeScreen === 'teacher-dashboard' && (
          <TeacherDashboard
            onNavigateToUpload={() => setActiveScreen('teacher-upload')}
            onBackToRoleSelect={() => setActiveScreen('role-select')}
          />
        )}

        {activeScreen === 'teacher-upload' && (
          <UploadContent
            onBackToDashboard={() => setActiveScreen('teacher-dashboard')}
            onSaveModule={() => setActiveScreen('teacher-dashboard')}
            onBackToRoleSelect={() => setActiveScreen('role-select')}
          />
        )}
      </div>
    </div>
  );
}
