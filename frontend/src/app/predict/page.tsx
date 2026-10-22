import React from 'react';
import Link from 'next/link';

export default function PredictPage() {
  return (
    <main style={{ maxWidth: '600px', margin: '40px auto', padding: '24px' }}>
      <h1>Property Price Prediction</h1>
      <p style={{ color: '#4b5563' }}>[PLANNED - Phase 5] Property input form based on approved feature schema.</p>
      <Link href="/" style={{ color: '#2563eb' }}>&larr; Back to Home</Link>
    </main>
  );
}
