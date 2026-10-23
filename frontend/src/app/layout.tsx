import type { Metadata } from 'next';
import React from 'react';
import './globals.css';
import { AuthProvider } from '../context/AuthContext';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

export const metadata: Metadata = {
  title: 'GharScope — Know the Value. Find Your Place.',
  description:
    'Objective, data-driven residential real estate price estimates across 81 Indian micro-markets powered by machine learning.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AuthProvider>
          <Navbar />
          <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>{children}</main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
