export type UserRole = 'teacher' | 'student' | null;

export type ActiveScreen = 
  | 'role-select'
  | 'student-login'
  | 'learning-path'
  | 'quiz'
  | 'teacher-dashboard'
  | 'teacher-upload';

export interface StudentProfile {
  fullName: string;
  studentId: string;
}

export interface QuizOption {
  id: string;
  label: string;
  text: string;
}

export interface Question {
  id: number;
  type: 'multiple-choice' | 'fill-in-blanks';
  question: string;
  options?: QuizOption[];
  correctAnswer: string;
  reference?: string;
  formula?: string;
  explanation?: string;
  acceptableAnswers?: string[];
}

export interface StudentPerformance {
  id: string;
  name: string;
  mssv: string;
  grade: number;
  status: 'On Track' | 'At Risk' | 'Needs Review';
  avatarInitials: string;
}
