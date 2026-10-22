import React from 'react';
import Link from 'next/link';

export default function AdminPage() {
  return (
    <main style={{ maxWidth: '900px', margin: '40px auto', padding: '24px' }}>
      <h1>Administrator Control Panel</h1>
      <p style={{ color: '#4b5563' }}>[PLANNED - Phase 5] Database-backed prediction summaries, user management, and date-range reporting.</p>
      <Link href="/" style={{ color: '#2563eb' }}>&larr; Back to Home</Link>
    </main>
  );
}
