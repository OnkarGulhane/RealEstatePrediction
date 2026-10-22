import React from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <main style={{ maxWidth: '800px', margin: '40px auto', padding: '24px' }}>
      <h1>User Dashboard</h1>
      <p style={{ color: '#4b5563' }}>[PLANNED - Phase 5] Personal prediction history and user profile management.</p>
      <Link href="/" style={{ color: '#2563eb' }}>&larr; Back to Home</Link>
    </main>
  );
}
