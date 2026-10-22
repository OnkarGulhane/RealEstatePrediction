import React from 'react';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <main style={{ maxWidth: '400px', margin: '40px auto', padding: '24px' }}>
      <h1>Sign In</h1>
      <p style={{ color: '#4b5563' }}>[PLANNED - Phase 5] Authentication interface connecting to Django REST API.</p>
      <Link href="/" style={{ color: '#2563eb' }}>&larr; Back to Home</Link>
    </main>
  );
}
