import React from 'react';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <main style={{ maxWidth: '800px', margin: '40px auto', padding: '24px' }}>
      <h1>About — Real Estate Price Prediction</h1>
      <p style={{ color: '#4b5563' }}>[PLANNED - Phase 5] Public product information, ML overview, and limitation disclaimers.</p>
      <Link href="/" style={{ color: '#2563eb' }}>&larr; Back to Home</Link>
    </main>
  );
}
