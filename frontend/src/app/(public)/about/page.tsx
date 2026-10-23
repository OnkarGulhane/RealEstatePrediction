import React from 'react';
import Link from 'next/link';
import { Database, Layers, ArrowRight, AlertTriangle } from 'lucide-react';

export default function AboutPage() {
  return (
    <div style={{ paddingTop: '56px', paddingBottom: '80px', backgroundColor: 'var(--bg-page)' }}>
      <div className="container-wide">
        {/* Header */}
        <div style={{ maxWidth: '780px', marginBottom: '56px' }}>
          <span className="eyebrow" style={{ display: 'inline-block', marginBottom: '12px' }}>
            Methodology & Transparency
          </span>
          <h1
            className="font-display"
            style={{
              fontSize: 'var(--text-h1)',
              fontWeight: 600,
              color: 'var(--color-dark)',
              lineHeight: 1.15,
              marginBottom: '16px',
            }}
          >
            How GharScope Computes Property Values
          </h1>
          <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Transparent real estate intelligence. Understand how our supervised machine learning algorithms evaluate residential listings across 81 Indian micro-markets.
          </p>
        </div>

        {/* Canonical Offline Metrics Grid */}
        <div style={{ marginBottom: '64px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
            <h2
              className="font-display"
              style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-dark)', margin: 0 }}
            >
              Offline Model Evaluation (Fixed Holdout Partition)
            </h2>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              Evaluated on 9,789 unseen test records
            </span>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '20px',
            }}
          >
            {/* Metric 1: R² */}
            <div className="card-surface">
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Holdout R² Score
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-primary)', margin: '8px 0 4px' }}>
                0.7104
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Explains 71.04% of price variance on unseen test listings.
              </p>
            </div>

            {/* Metric 2: MAE */}
            <div className="card-surface">
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Mean Absolute Error (MAE)
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-dark)', margin: '8px 0 4px' }}>
                ₹26.94 L
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Average holdout absolute discrepancy on continuous INR target.
              </p>
            </div>

            {/* Metric 3: RMSE */}
            <div className="card-surface">
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Root Mean Squared Error (RMSE)
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-primary)', margin: '8px 0 4px' }}>
                ₹85.18 L
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Standard deviation of holdout residuals; penalizes larger errors.
              </p>
            </div>

            {/* Metric 4: Improvement */}
            <div className="card-surface">
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Baseline Improvement
              </span>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-success)', margin: '8px 0 4px' }}>
                +56.91%
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                Gain over naive DummyRegressor baseline (Median AE: ₹11.06 L).
              </p>
            </div>
          </div>
        </div>

        {/* Detailed Sections (2-Column) */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '40px',
            marginBottom: '64px',
          }}
        >
          {/* Card 1: Machine Learning Architecture */}
          <div className="card-surface">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(16, 61, 50, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <Database size={18} />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-dark)' }}>
                Active Machine Learning Model
              </h3>
            </div>
            <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '16px' }}>
              GharScope deploys a tuned <strong>HistGradientBoostingRegressor</strong> trained on historical continuous asking prices in Indian Rupees (INR).
            </p>
            <ul style={{ paddingLeft: '20px', fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              <li><strong>Log-target transformation:</strong> Addresses the heavy right skew inherent in luxury and high-value Indian urban real estate.</li>
              <li><strong>Categorical handling:</strong> Evaluates micro-market, furnishing, ownership, and transaction type natively without arbitrary numerical encoding.</li>
              <li><strong>Treatment B Parking Logic:</strong> Incorporates verified parking spaces with non-zero defaults where indicated by property tier.</li>
            </ul>
          </div>

          {/* Card 2: Area Standards (Carpet vs Super) */}
          <div className="card-surface">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <div
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'rgba(201, 165, 106, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#8C6A30',
                }}
              >
                <Layers size={18} />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-dark)' }}>
                Carpet Area vs. Super Built-up Area
              </h3>
            </div>
            <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '16px' }}>
              Indian residential real estate quotes prices in both formats. GharScope explicitly normalizes them:
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              <div style={{ padding: '12px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-xs)' }}>
                <strong style={{ color: 'var(--color-primary)' }}>Carpet Area: </strong>
                The actual net usable floor space bounded by the inner walls of the apartment.
              </div>
              <div style={{ padding: '12px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-xs)' }}>
                <strong style={{ color: 'var(--color-dark)' }}>Super Built-up Area: </strong>
                The total saleable area including carpet area plus proportionate shares of common areas (corridors, lifts, clubhouse, staircase).
              </div>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Card */}
        <div
          style={{
            backgroundColor: '#FFFBEB',
            border: '1px solid #FDE68A',
            borderRadius: 'var(--radius-md)',
            padding: '24px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '16px',
          }}
        >
          <AlertTriangle size={24} color="#B45309" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#92400E', marginBottom: '6px' }}>
              Statistical Guidance Notice
            </h4>
            <p style={{ fontSize: '0.875rem', color: '#78350F', lineHeight: 1.6 }}>
              GharScope estimates are generated through algorithmic inference and reflect statistical central tendencies from historical data. They are not physical home inspections, chartered surveyor valuations, legal title guarantees, or bank lending assurances. Buyers and sellers should conduct independent on-site due diligence.
            </p>
          </div>
        </div>

        {/* Bottom CTA */}
        <div style={{ textAlign: 'center', marginTop: '56px' }}>
          <Link href="/predict" className="btn-primary" style={{ height: '50px', padding: '0 28px' }}>
            <span>Calculate Property Value</span>
            <ArrowRight size={18} />
          </Link>
        </div>
      </div>
    </div>
  );
}
