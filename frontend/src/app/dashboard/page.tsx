'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../context/AuthContext';
import { apiFetch, ApiClientError } from '../../lib/api-client';
import { formatINRLakhCrore, formatINRExact, formatPricePerSqFt, formatDateIST } from '../../lib/formatters';
import type { PaginatedPredictionList, PredictionRecord } from '../../types';
import {
  History,
  Calculator,
  Eye,
  X,
  AlertCircle,
  ArrowRight,
  Building,
  RotateCcw,
} from 'lucide-react';

export default function DashboardPage() {
  const { user, authReady } = useAuth();

  const [predictions, setPredictions] = useState<PredictionRecord[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Detail Modal State
  const [selectedRecord, setSelectedRecord] = useState<PredictionRecord | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<PaginatedPredictionList>('/predictions/?page=1&page_size=50');
      setPredictions(data.results || []);
      setTotalCount(data.count || 0);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message || 'Failed to load prediction history.');
      } else {
        setError('A network error occurred while fetching your history.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authReady && user) {
      fetchHistory();
    }
  }, [authReady, user]);

  const openDetail = async (id: string) => {
    try {
      const record = await apiFetch<PredictionRecord>(`/predictions/${id}/`);
      setSelectedRecord(record);
    } catch {
      // Fallback to local list item if network request fails
      const local = predictions.find((p) => p.id === id);
      if (local) setSelectedRecord(local);
    }
  };

  if (!authReady) {
    return (
      <div style={{ padding: '80px 20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading session...
      </div>
    );
  }

  if (!user) {
    return (
      <div style={{ paddingTop: '64px', paddingBottom: '80px', backgroundColor: 'var(--bg-page)' }}>
        <div className="container-reading">
          <div className="card-surface" style={{ textAlign: 'center', padding: '48px 32px' }}>
            <History size={40} color="var(--color-primary)" style={{ marginBottom: '16px' }} />
            <h1 className="font-display" style={{ fontSize: '1.75rem', fontWeight: 600, marginBottom: '12px' }}>
              Sign In to View Your Valuations
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              Your prediction history is privately encrypted and associated with your account.
            </p>
            <Link href="/login?returnUrl=/dashboard" className="btn-primary" style={{ padding: '0 24px' }}>
              <span>Sign In to Your Dashboard</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ paddingTop: '48px', paddingBottom: '80px', backgroundColor: 'var(--bg-page)' }}>
      <div className="container-wide">
        {/* Header */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '20px',
            marginBottom: '36px',
          }}
        >
          <div>
            <span className="eyebrow" style={{ display: 'inline-block', marginBottom: '8px' }}>
              Authenticated Dashboard
            </span>
            <h1
              className="font-display"
              style={{ fontSize: 'var(--text-h1)', fontWeight: 600, color: 'var(--color-dark)', lineHeight: 1.15 }}
            >
              My Valuation History
            </h1>
            <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Signed in as <strong>{user.email}</strong> ({totalCount} total estimates saved)
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={fetchHistory}
              className="btn-secondary"
              style={{ height: '44px', padding: '0 16px' }}
              title="Refresh History"
            >
              <RotateCcw size={16} />
              <span>Refresh</span>
            </button>
            <Link href="/predict" className="btn-primary" style={{ height: '44px', padding: '0 20px' }}>
              <Calculator size={16} />
              <span>New Valuation</span>
            </Link>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="alert-banner alert-error" style={{ marginBottom: '24px' }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>{error}</div>
          </div>
        )}

        {/* Loading Skeleton */}
        {loading ? (
          <div className="card-surface" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Retrieving past property estimates from database...
          </div>
        ) : predictions.length === 0 ? (
          /* Empty State */
          <div
            className="card-surface"
            style={{
              textAlign: 'center',
              padding: '64px 32px',
              backgroundColor: 'var(--color-surface)',
              border: '1px dashed var(--border-default)',
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                backgroundColor: 'rgba(16, 61, 50, 0.08)',
                color: 'var(--color-primary)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '20px',
              }}
            >
              <Building size={32} />
            </div>
            <h2 className="font-display" style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '8px' }}>
              No Valuations Recorded Yet
            </h2>
            <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto 24px', lineHeight: 1.6 }}>
              You haven&apos;t run any property estimates yet. Use our valuation calculator to evaluate continuous INR asking prices across 81 Indian micro-markets.
            </p>
            <Link href="/predict" className="btn-primary" style={{ height: '48px', padding: '0 24px' }}>
              <span>Run Your First Valuation</span>
              <ArrowRight size={18} />
            </Link>
          </div>
        ) : (
          /* Table of Predictions */
          <div className="card-surface" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ overflowX: 'auto' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  textAlign: 'left',
                  fontSize: '0.9375rem',
                }}
              >
                <thead>
                  <tr
                    style={{
                      backgroundColor: 'var(--color-surface-subtle)',
                      borderBottom: '1px solid var(--border-default)',
                      color: 'var(--text-secondary)',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                    }}
                  >
                    <th style={{ padding: '16px 20px' }}>Date</th>
                    <th style={{ padding: '16px 20px' }}>Location</th>
                    <th style={{ padding: '16px 20px' }}>Property Spec</th>
                    <th style={{ padding: '16px 20px' }}>Estimate (INR)</th>
                    <th style={{ padding: '16px 20px' }}>Unit Rate</th>
                    <th style={{ padding: '16px 20px', textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.map((p) => (
                    <tr
                      key={p.id}
                      style={{
                        borderBottom: '1px solid var(--border-default)',
                        transition: 'background-color var(--duration-fast)',
                      }}
                    >
                      <td style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        {formatDateIST(p.created_at)}
                      </td>
                      <td style={{ padding: '16px 20px', fontWeight: 600, color: 'var(--color-dark)' }}>
                        <div>{p.location}</div>
                        {p.sub_area && (
                          <div style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--color-gold-warm, #B8860B)', marginTop: '2px' }}>
                            {p.sub_area}
                          </div>
                        )}
                      </td>
                      <td style={{ padding: '16px 20px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        {p.bhk ? `${p.bhk} BHK` : '—'} • {p.area_value} sq.ft. ({p.area_basis})
                      </td>
                      <td style={{ padding: '16px 20px' }}>
                        <span style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--color-primary)' }}>
                          {formatINRLakhCrore(p.estimated_price_inr)}
                        </span>
                      </td>
                      <td style={{ padding: '16px 20px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        {formatPricePerSqFt(p.estimated_price_inr, p.area_value)}
                      </td>
                      <td style={{ padding: '16px 20px', textAlign: 'right' }}>
                        <button
                          onClick={() => openDetail(p.id)}
                          className="btn-secondary"
                          style={{ height: '34px', padding: '0 12px', fontSize: '0.8125rem' }}
                        >
                          <Eye size={14} />
                          <span>View Details</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Detail Modal View */}
        {selectedRecord && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(10, 38, 31, 0.65)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px',
              zIndex: 100,
            }}
            onClick={() => setSelectedRecord(null)}
          >
            <div
              className="card-surface"
              style={{
                width: '100%',
                maxWidth: '560px',
                padding: '36px',
                position: 'relative',
                boxShadow: 'var(--shadow-modal)',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setSelectedRecord(null)}
                style={{
                  position: 'absolute',
                  top: '20px',
                  right: '20px',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                }}
                aria-label="Close Modal"
              >
                <X size={22} />
              </button>

              <span className="badge badge-gold" style={{ marginBottom: '12px' }}>
                Prediction Details
              </span>

              <h2 className="font-display" style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-dark)', marginBottom: '4px' }}>
                {selectedRecord.sub_area ? `${selectedRecord.location} (${selectedRecord.sub_area})` : selectedRecord.location} Valuation
              </h2>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
                Generated on {formatDateIST(selectedRecord.created_at)} • Record ID: {selectedRecord.id.slice(0, 8)}...
              </p>

              {/* Estimate Display */}
              <div
                style={{
                  backgroundColor: 'var(--color-surface-subtle)',
                  padding: '20px',
                  borderRadius: 'var(--radius-sm)',
                  marginBottom: '24px',
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Model Estimated Valuation
                </div>
                <div style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--color-primary)', lineHeight: 1.1, margin: '4px 0' }}>
                  {formatINRLakhCrore(selectedRecord.estimated_price_inr)}
                </div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  Exact: {formatINRExact(selectedRecord.estimated_price_inr)} ({formatPricePerSqFt(selectedRecord.estimated_price_inr, selectedRecord.area_value)})
                </div>
              </div>

              {/* Attributes Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '12px',
                  fontSize: '0.875rem',
                  marginBottom: '24px',
                }}
              >
                {selectedRecord.sub_area && (
                  <div style={{ gridColumn: 'span 2' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Neighborhood:</span> <strong>{selectedRecord.sub_area}</strong>
                  </div>
                )}
                <div><span style={{ color: 'var(--text-muted)' }}>Area:</span> <strong>{selectedRecord.area_value} sq.ft.</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Area Basis:</span> <strong>{selectedRecord.area_basis}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Layout:</span> <strong>{selectedRecord.bhk ? `${selectedRecord.bhk} BHK` : '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Bathrooms:</span> <strong>{selectedRecord.bathrooms || '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Balcony:</span> <strong>{selectedRecord.balcony ?? '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Parking Spaces:</span> <strong>{selectedRecord.parking_spaces ?? '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Floor:</span> <strong>{selectedRecord.floor_number ?? '—'} of {selectedRecord.total_floors ?? '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Furnishing:</span> <strong>{selectedRecord.furnishing || '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Facing:</span> <strong>{selectedRecord.facing || '—'}</strong></div>
                <div><span style={{ color: 'var(--text-muted)' }}>Ownership:</span> <strong>{selectedRecord.ownership || '—'}</strong></div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <button onClick={() => setSelectedRecord(null)} className="btn-secondary" style={{ padding: '0 20px' }}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
