import type { Metadata } from 'next';
import React from 'react';

export const metadata: Metadata = {
  title: 'Real Estate Price Prediction Platform — Scaffold',
  description: 'Scaffold state for the Indian residential real estate price prediction web application.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'system-ui, -apple-system, sans-serif', margin: 0, padding: 0, backgroundColor: '#f9fafb', color: '#111827' }}>
        {children}
      </body>
    </html>
  );
}
