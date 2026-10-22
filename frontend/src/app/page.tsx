import React from 'react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <main style={{ maxWidth: '800px', margin: '40px auto', padding: '24px', backgroundColor: '#ffffff', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <header style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '16px', marginBottom: '24px' }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '24px', color: '#1f2937' }}>
          Real Estate Price Prediction Platform — India
        </h1>
        <span style={{ display: 'inline-block', padding: '4px 8px', borderRadius: '4px', backgroundColor: '#fef3c7', color: '#92400e', fontSize: '12px', fontWeight: 600 }}>
          SCAFFOLD STATE — PHASE 0 PLANNING
        </span>
      </header>

      <section style={{ lineHeight: '1.6', color: '#4b5563', marginBottom: '24px' }}>
        <p>
          This is the minimal repository scaffold for the <strong>Real Estate Price Prediction Platform</strong>.
          Product features (user authentication, property price prediction forms, prediction history, and administrator dashboards) are planned for implementation in subsequent phases following formal product-owner approval.
        </p>
      </section>

      <section style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '6px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '16px', margin: '0 0 12px 0', color: '#374151' }}>Scaffold Route Placeholders</h2>
        <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
          <li><Link href="/about" style={{ color: '#2563eb' }}>/about</Link> — Public information placeholder</li>
          <li><Link href="/login" style={{ color: '#2563eb' }}>/login</Link> — Authentication placeholder</li>
          <li><Link href="/predict" style={{ color: '#2563eb' }}>/predict</Link> — Prediction form placeholder</li>
          <li><Link href="/dashboard" style={{ color: '#2563eb' }}>/dashboard</Link> — User dashboard placeholder</li>
          <li><Link href="/admin" style={{ color: '#2563eb' }}>/admin</Link> — Administrator dashboard placeholder</li>
        </ul>
      </section>

      <footer style={{ borderTop: '1px solid #e5e7eb', paddingTop: '12px', fontSize: '13px', color: '#6b7280' }}>
        Status: Scaffold initialized. Backend API configured to <code>http://localhost:8000/api/v1</code>.
      </footer>
    </main>
  );
}
