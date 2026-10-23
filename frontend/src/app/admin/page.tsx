'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../../context/AuthContext';
import { apiFetch, ApiClientError } from '../../lib/api-client';
import { formatINRLakhCrore } from '../../lib/formatters';
import type { AdminSummaryResponse, AdminModelMetadataResponse } from '../../types';
import {
  ShieldAlert,
  ShieldCheck,
  Users,
  Database,
  BarChart3,
  Activity,
  RotateCcw,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';

export default function AdminPage() {
  const { user, authReady } = useAuth();

  const [summary, setSummary] = useState<AdminSummaryResponse | null>(null);
  const [modelMeta, setModelMeta] = useState<AdminModelMetadataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAdminData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, modelData] = await Promise.all([
        apiFetch<AdminSummaryResponse>('/admin/summary/'),
        apiFetch<AdminModelMetadataResponse>('/admin/model/'),
      ]);
      setSummary(summaryData);
      setModelMeta(modelData);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message || 'Failed to load administrator telemetry.');
      } else {
        setError('A network error occurred while accessing the admin telemetry.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authReady && user?.is_staff) {
      fetchAdminData();
    }
  }, [authReady, user]);

  if (!authReady) {
    return (
      <div style={{ padding: '80px 20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Verifying administrator credentials...
      </div>
    );
  }

  // Non-Staff or Unauthenticated Access Guard
  if (!user || !user.is_staff) {
    return (
      <div style={{ paddingTop: '64px', paddingBottom: '80px', backgroundColor: 'var(--bg-page)' }}>
        <div className="container-reading">
          <div className="card-surface" style={{ textAlign: 'center', padding: '48px 32px' }}>
            <ShieldAlert size={48} color="var(--color-error)" style={{ marginBottom: '16px' }} />
            <h1 className="font-display" style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--color-dark)', marginBottom: '12px' }}>
              Staff Authorization Required (403)
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.6 }}>
              {user
                ? `The account ${user.email} is registered as a regular member and lacks is_staff permissions required to access the admin portal.`
                : 'You must sign in with a staff administrator account to access platform metrics and telemetry.'}
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
              <Link href="/login?returnUrl=/admin" className="btn-primary" style={{ padding: '0 24px' }}>
                <span>Sign in as Staff</span>
                <ArrowRight size={16} />
              </Link>
              <Link href="/" className="btn-secondary" style={{ padding: '0 20px' }}>
                Return Home
              </Link>
            </div>
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-forest">Authorized Portal</span>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Staff Telemetry</span>
            </div>
            <h1
              className="font-display"
              style={{ fontSize: 'var(--text-h1)', fontWeight: 600, color: 'var(--color-dark)', lineHeight: 1.15 }}
            >
              Platform Telemetry & Operations
            </h1>
            <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Live metrics from Django database & FastAPI inference microservice
            </p>
          </div>

          <button
            onClick={fetchAdminData}
            className="btn-secondary"
            style={{ height: '44px', padding: '0 16px' }}
            title="Refresh Telemetry"
          >
            <RotateCcw size={16} />
            <span>Refresh Telemetry</span>
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="alert-banner alert-error" style={{ marginBottom: '24px' }}>
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>{error}</div>
          </div>
        )}

        {loading ? (
          <div className="card-surface" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Polling administrator APIs...
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
            {/* KPI Cards Grid */}
            {summary && (
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-dark)', marginBottom: '16px' }}>
                  Live System KPIs
                </h2>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                    gap: '20px',
                  }}
                >
                  <div className="card-surface">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                        Registered Users
                      </span>
                      <Users size={18} color="var(--color-primary)" />
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-dark)', margin: '8px 0 4px' }}>
                      {summary.users.total}
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      {summary.users.active} active • {summary.users.staff} staff
                    </div>
                  </div>

                  <div className="card-surface">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                        Total Predictions
                      </span>
                      <Activity size={18} color="var(--color-primary)" />
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-dark)', margin: '8px 0 4px' }}>
                      {summary.predictions.total}
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      {summary.predictions.last_24_hours} past 24h • {summary.predictions.last_7_days} past 7d
                    </div>
                  </div>

                  <div className="card-surface">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                        Estimated Volume
                      </span>
                      <BarChart3 size={18} color="var(--color-primary)" />
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-primary)', margin: '8px 0 4px' }}>
                      {formatINRLakhCrore(summary.predictions.total_volume_inr)}
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      Total continuous valuation pool
                    </div>
                  </div>

                  <div className="card-surface">
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                        Average Price
                      </span>
                      <Database size={18} color="var(--color-primary)" />
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--color-dark)', margin: '8px 0 4px' }}>
                      {formatINRLakhCrore(summary.predictions.average_price_inr)}
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      Mean estimated residential price
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Model Telemetry Panel */}
            {modelMeta && (
              <div className="card-surface">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <ShieldCheck size={20} color="var(--color-primary)" />
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--color-dark)' }}>
                    Active Machine Learning Artifact Telemetry
                  </h2>
                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '20px',
                    marginBottom: '20px',
                  }}
                >
                  <div style={{ padding: '16px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-xs)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Model Identifier</div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-dark)', marginTop: '4px' }}>
                      {modelMeta.model_id}
                    </div>
                  </div>

                  <div style={{ padding: '16px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-xs)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Algorithm Pipeline</div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--color-dark)', marginTop: '4px' }}>
                      {modelMeta.algorithm}
                    </div>
                  </div>

                  <div style={{ padding: '16px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-xs)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Holdout R² Score</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-primary)', marginTop: '4px' }}>
                      {modelMeta.test_evaluation.r2_score}
                    </div>
                  </div>

                  <div style={{ padding: '16px', backgroundColor: 'var(--color-surface-subtle)', borderRadius: 'var(--radius-xs)' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Holdout MAE (INR)</div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--color-dark)', marginTop: '4px' }}>
                      {formatINRLakhCrore(modelMeta.test_evaluation.mae_inr)}
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                  {modelMeta.disclaimer}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
