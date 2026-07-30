import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VLearn EduAI — Sinh Bài Tập Tự Động & Báo Cáo Lỗ Hổng Kiến Thức",
  description: "Nền tảng AI Agent & RAG Pipeline tự động hóa sinh bài tập và phân tích lỗ hổng kiến thức học viên sau bài giảng.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="bg-slate-950 text-slate-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}
