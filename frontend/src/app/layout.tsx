import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Sidebar from '@/components/Sidebar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'TrialGuard AI',
  description: 'Agentic Clinical Trial Document Validation Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Sidebar />
        <main className="lg:ml-[280px] min-h-screen dot-grid mesh-gradient p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
