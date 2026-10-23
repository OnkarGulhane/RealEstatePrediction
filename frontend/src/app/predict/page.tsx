'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '../../context/AuthContext';
import { apiFetch, ApiClientError } from '../../lib/api-client';
import { formatINRLakhCrore, formatPricePerSqFt } from '../../lib/formatters';
import type { LocationsMetadataResponse, LocationItem, PredictionRecord } from '../../types';
import {
  Home,
  MapPin,
  Maximize2,
  Bed,
  Bath,
  BarChart2,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';

export default function PredictPage() {
  const { user } = useAuth();

  // Locations state
  const [locations, setLocations] = useState<LocationItem[]>([]);
  const [locationsLoading, setLocationsLoading] = useState(true);

  // Form Fields
  const [location, setLocation] = useState('');
  const [propertyType, setPropertyType] = useState('Apartment');
  const [areaValue, setAreaValue] = useState<number | ''>(1150);
  const [areaBasis, setAreaBasis] = useState<'CARPET' | 'SUPER'>('CARPET');
  const [bhk, setBhk] = useState<number | ''>(2);
  const [bathrooms, setBathrooms] = useState<number | ''>(2);
  const [parkingSpaces, setParkingSpaces] = useState<number | ''>(1);
  const [floorNumber, setFloorNumber] = useState<number | ''>(3);
  const [totalFloors, setTotalFloors] = useState<number | ''>(10);
  const [furnishing, setFurnishing] = useState('Semi-Furnished');
  const [transactionType, setTransactionType] = useState('Resale');
  const [status, setStatus] = useState('Ready to Move');
  const [facing, setFacing] = useState('East');
  const [ownership, setOwnership] = useState('Freehold');

  // Submission state
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});
  const [result, setResult] = useState<PredictionRecord | null>(null);

  // Invalidate previous result when form inputs are modified to prevent stale data
  const handleFieldChange = <T,>(setter: (val: T) => void, val: T) => {
    setter(val);
    if (result) setResult(null);
    if (formError) setFormError(null);
  };

  // Pre-fill from query parameters if arriving from Catalogue
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const qLocation = params.get('location');
    const qType = params.get('type');
    const qArea = params.get('area');
    const qBhk = params.get('bhk');

    if (qLocation) setLocation(qLocation);
    if (qType) setPropertyType(qType);
    if (qArea && !Number.isNaN(Number(qArea))) setAreaValue(Number(qArea));
    if (qBhk && !Number.isNaN(Number(qBhk))) setBhk(Number(qBhk));
  }, []);

  // Load locations from backend
  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch<LocationsMetadataResponse>('/locations/');
        setLocations(data.locations || []);
        if (data.locations?.length > 0 && !location) {
          const defaultLoc = data.locations.find((l) => l.name === 'Bangalore') || data.locations[0];
          setLocation(defaultLoc.name);
        }
      } catch {
        // Fallback gracefully
      } finally {
        setLocationsLoading(false);
      }
    }
    load();
  }, [location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFieldErrors({});

    if (!user) {
      setFormError('Authentication required: Please sign in to execute and record official property valuations.');
      return;
    }

    if (!location) {
      setFormError('Please select a supported micro-market.');
      return;
    }

    if (!areaValue || Number(areaValue) < 100 || Number(areaValue) > 20000) {
      setFormError('Area value must be between 100 and 20,000 sq.ft.');
      setFieldErrors({ area_value: ['Must be between 100 and 20,000 sq.ft.'] });
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        schema_version: '1.0' as const,
        location,
        area_value: Number(areaValue),
        area_basis: areaBasis,
        bhk: bhk !== '' ? Number(bhk) : null,
        bathrooms: bathrooms !== '' ? Number(bathrooms) : null,
        balcony: 1,
        floor_number: floorNumber !== '' ? Number(floorNumber) : null,
        total_floors: totalFloors !== '' ? Number(totalFloors) : null,
        parking_spaces: parkingSpaces !== '' ? Number(parkingSpaces) : null,
        furnishing: furnishing || null,
        transaction_type: transactionType || null,
        status: status || null,
        facing: facing || null,
        ownership: ownership || null,
      };

      const record = await apiFetch<PredictionRecord>('/predictions/', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setResult(record);
      window.scrollTo({ top: 180, behavior: 'smooth' });
    } catch (err) {
      if (err instanceof ApiClientError) {
        if (err.status === 401) {
          setFormError('Authentication required: Please sign in to run and record official property valuations.');
        } else if (err.status === 503) {
          setFormError('Machine learning inference service is currently warming up. Please retry in a few seconds.');
        } else if (err.status === 504) {
          setFormError('Valuation calculation timed out. The ML service took too long to respond. Please retry.');
        } else {
          setFormError(err.message || 'Validation error: Please review the highlighted property specifications.');
        }
        if (err.fields) {
          setFieldErrors(err.fields);
        }
      } else {
        setFormError('Network error occurred while connecting to the valuation engine.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ backgroundColor: 'var(--color-ivory)', minHeight: 'calc(100vh - var(--header-height))', paddingBottom: '80px' }}>
      <div className="container-wide" style={{ paddingTop: '36px' }}>

        {/* PAGE HEADER matching 3. Property Price Prediction (Final Design) */}
        <div style={{ maxWidth: '640px', marginBottom: '36px' }}>
          <span
            className="eyebrow"
            style={{
              display: 'inline-block',
              marginBottom: '10px',
              color: 'var(--color-primary)',
              letterSpacing: '0.08em',
            }}
          >
            PROPERTY VALUATION
          </span>
          <h1
            className="font-display"
            style={{
              fontSize: 'clamp(2rem, 3.5vw, 2.75rem)',
              fontWeight: 600,
              color: 'var(--color-dark)',
              lineHeight: 1.15,
              marginBottom: '12px',
            }}
          >
            Predict Your<br />
            Property&apos;s Value
          </h1>
          <p
            style={{
              fontSize: '1rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Enter the details below to get an estimated property price using our ML model.
          </p>
        </div>

        {/* MAIN SPLIT: Form on Left (White), Contrast Panel on Right (Dark Green) */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
            gap: '40px',
            alignItems: 'flex-start',
            marginBottom: '64px',
          }}
        >
          {/* LEFT: Valuation Input Form */}
          <div
            className="card-surface"
            style={{
              padding: '36px 32px',
            }}
          >
            {!user && (
              <div
                className="alert-banner alert-warning"
                style={{
                  marginBottom: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <AlertCircle size={18} style={{ flexShrink: 0 }} />
                  <span style={{ fontSize: '0.84375rem' }}>
                    Sign in is required to run and record official property valuations.
                  </span>
                </div>
                <Link
                  href="/login?returnUrl=/predict"
                  className="btn-primary"
                  style={{
                    height: '32px',
                    padding: '0 12px',
                    fontSize: '0.75rem',
                    whiteSpace: 'nowrap',
                    flexShrink: 0,
                  }}
                >
                  Sign In
                </Link>
              </div>
            )}

            {formError && (
              <div className="alert-banner alert-error" style={{ marginBottom: '24px' }}>
                <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Property Type */}
              <div className="form-group">
                <label className="form-label" htmlFor="prop-type">
                  Property Type
                </label>
                <select
                  id="prop-type"
                  value={propertyType}
                  onChange={(e) => handleFieldChange(setPropertyType, e.target.value)}
                  className="form-select"
                >
                  <option value="Apartment">Apartment</option>
                  <option value="Independent House">Independent House</option>
                  <option value="Villa">Villa</option>
                  <option value="Residential Plot">Residential Plot</option>
                </select>
              </div>

              {/* Location */}
              <div className="form-group">
                <label className="form-label" htmlFor="prop-location">
                  Location (81 Micro-Markets)
                </label>
                <div style={{ position: 'relative' }}>
                  <select
                    id="prop-location"
                    value={location}
                    onChange={(e) => handleFieldChange(setLocation, e.target.value)}
                    className="form-select"
                    style={{ paddingLeft: '38px' }}
                    disabled={locationsLoading}
                  >
                    {locations.map((loc) => (
                      <option key={loc.normalized || loc.name} value={loc.name}>
                        {loc.name}
                      </option>
                    ))}
                  </select>
                  <MapPin
                    size={16}
                    color="var(--text-secondary)"
                    style={{ position: 'absolute', left: '12px', top: '16px', pointerEvents: 'none' }}
                  />
                </div>
              </div>

              {/* Area (sq.ft.) and Area Basis */}
              <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label" htmlFor="areaValue">
                    Area (sq.ft.) <span style={{ color: 'var(--color-error)' }}>*</span>
                  </label>
                  <input
                    id="areaValue"
                    type="number"
                    min="100"
                    max="20000"
                    required
                    value={areaValue}
                    onChange={(e) => handleFieldChange(setAreaValue, e.target.value === '' ? '' : Number(e.target.value))}
                    className="form-input"
                    placeholder="e.g. 1150"
                  />
                  {fieldErrors['area_value'] && (
                    <span className="field-error" style={{ fontSize: '0.75rem', color: 'var(--color-error)', marginTop: '4px', display: 'block' }}>
                      {fieldErrors['area_value'].join(' ')}
                    </span>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Area Basis</label>
                  <div className="segmented-group">
                    <button
                      type="button"
                      className={`segmented-option ${areaBasis === 'CARPET' ? 'active' : ''}`}
                      onClick={() => handleFieldChange(setAreaBasis, 'CARPET')}
                      style={{ flex: 1, height: '40px', fontSize: '0.8125rem' }}
                    >
                      Carpet
                    </button>
                    <button
                      type="button"
                      className={`segmented-option ${areaBasis === 'SUPER' ? 'active' : ''}`}
                      onClick={() => handleFieldChange(setAreaBasis, 'SUPER')}
                      style={{ flex: 1, height: '40px', fontSize: '0.8125rem' }}
                    >
                      Super
                    </button>
                  </div>
                </div>
              </div>

              {/* Bedrooms & Bathrooms */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label" htmlFor="bhk-select">
                    Bedrooms
                  </label>
                  <select
                    id="bhk-select"
                    value={bhk}
                    onChange={(e) => handleFieldChange(setBhk, e.target.value === '' ? '' : Number(e.target.value))}
                    className="form-select"
                  >
                    {[1, 2, 3, 4, 5, 6].map((n) => (
                      <option key={n} value={n}>
                        {n} BHK
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="bath-select">
                    Bathroom
                  </label>
                  <select
                    id="bath-select"
                    value={bathrooms}
                    onChange={(e) => handleFieldChange(setBathrooms, e.target.value === '' ? '' : Number(e.target.value))}
                    className="form-select"
                  >
                    {[1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Parking Spaces & Floor */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div className="form-group">
                  <label className="form-label" htmlFor="parking-spaces">
                    Parking Spaces
                  </label>
                  <select
                    id="parking-spaces"
                    value={parkingSpaces}
                    onChange={(e) => handleFieldChange(setParkingSpaces, e.target.value === '' ? '' : Number(e.target.value))}
                    className="form-select"
                  >
                    {[0, 1, 2, 3, 4, 5].map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="floor-no">
                    Floor Number
                  </label>
                  <input
                    id="floor-no"
                    type="number"
                    value={floorNumber}
                    onChange={(e) => handleFieldChange(setFloorNumber, e.target.value === '' ? '' : Number(e.target.value))}
                    className="form-input"
                    placeholder="3"
                  />
                </div>
              </div>

              {/* Collapsible Additional Specifications */}
              <details style={{ marginTop: '4px', borderTop: '1px solid var(--color-border-subtle)', paddingTop: '12px' }}>
                <summary style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-primary)', cursor: 'pointer', marginBottom: '14px' }}>
                  + Additional Property Specifications (Optional)
                </summary>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '8px' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="total-floors">Total Floors</label>
                    <input
                      id="total-floors"
                      type="number"
                      value={totalFloors}
                      onChange={(e) => handleFieldChange(setTotalFloors, e.target.value === '' ? '' : Number(e.target.value))}
                      className="form-input"
                      placeholder="10"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="furnishing-select">Furnishing</label>
                    <select
                      id="furnishing-select"
                      value={furnishing}
                      onChange={(e) => handleFieldChange(setFurnishing, e.target.value)}
                      className="form-select"
                    >
                      <option value="Furnished">Furnished</option>
                      <option value="Semi-Furnished">Semi-Furnished</option>
                      <option value="Unfurnished">Unfurnished</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="facing-select">Facing</label>
                    <select
                      id="facing-select"
                      value={facing}
                      onChange={(e) => handleFieldChange(setFacing, e.target.value)}
                      className="form-select"
                    >
                      <option value="East">East</option>
                      <option value="North">North</option>
                      <option value="West">West</option>
                      <option value="South">South</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="ownership-select">Ownership</label>
                    <select
                      id="ownership-select"
                      value={ownership}
                      onChange={(e) => handleFieldChange(setOwnership, e.target.value)}
                      className="form-select"
                    >
                      <option value="Freehold">Freehold</option>
                      <option value="Co-operative Society">Co-operative Society</option>
                      <option value="Leasehold">Leasehold</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="transaction-select">Transaction</label>
                    <select
                      id="transaction-select"
                      value={transactionType}
                      onChange={(e) => handleFieldChange(setTransactionType, e.target.value)}
                      className="form-select"
                    >
                      <option value="Resale">Resale</option>
                      <option value="New Property">New Property</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="status-select">Status</label>
                    <select
                      id="status-select"
                      value={status}
                      onChange={(e) => handleFieldChange(setStatus, e.target.value)}
                      className="form-select"
                    >
                      <option value="Ready to Move">Ready to Move</option>
                    </select>
                  </div>
                </div>
              </details>

              {/* Submit CTA */}
              <div style={{ marginTop: '12px' }}>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary"
                  style={{ width: '100%', height: '50px', fontSize: '1rem', fontWeight: 600 }}
                >
                  <span>{submitting ? 'Calculating ML Estimate...' : 'Get Valuation'}</span>
                  <ArrowRight size={17} />
                </button>
                {!user && (
                  <p style={{ textAlign: 'center', fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '8px' }}>
                    Note: <Link href="/login?returnUrl=/predict" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>Sign in</Link> required to save valuations to your permanent dashboard history.
                  </p>
                )}
              </div>
            </form>
          </div>

          {/* RIGHT: CONTRAST ESTIMATED VALUE PANEL (Deep Forest Green #0A261F) */}
          <div
            className="predict-result-panel"
            style={{
              backgroundColor: 'var(--color-primary-dark)',
              borderRadius: 'var(--radius-md)',
              padding: '36px 32px',
              color: '#FFFFFF',
              boxShadow: 'var(--shadow-card)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {submitting ? (
              /* LOADING STATE */
              <div style={{ padding: '48px 16px', textAlign: 'center' }}>
                <div
                  style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(212, 175, 55, 0.15)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-gold)',
                    margin: '0 auto 24px',
                    animation: 'spin 1.4s linear infinite',
                  }}
                >
                  <BarChart2 size={28} />
                </div>
                <h3
                  className="font-display"
                  style={{ fontSize: '1.5rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '10px' }}
                >
                  Calculating Valuation...
                </h3>
                <p style={{ fontSize: '0.9375rem', color: '#CBD5E1', maxWidth: '360px', margin: '0 auto 20px', lineHeight: 1.55 }}>
                  Evaluating {areaValue || 1150} sq.ft. {propertyType} in {location || 'selected market'} against our verified machine learning model...
                </p>
                <div style={{ display: 'inline-block', fontSize: '0.75rem', color: 'var(--color-gold)', letterSpacing: '0.06em', textTransform: 'uppercase', fontWeight: 600 }}>
                  Model: HistGradientBoosting (Holdout R² = 0.7104)
                </div>
              </div>
            ) : result ? (
              /* SUCCESSFUL VALUATION STATE */
              <div>
                {/* Top Row: Tag on left, Building thumbnail on right */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '20px',
                  }}
                >
                  <div>
                    <span
                      style={{
                        display: 'inline-block',
                        fontSize: '0.6875rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        color: 'var(--color-gold)',
                        marginBottom: '8px',
                      }}
                    >
                      ESTIMATED VALUE
                    </span>

                    {/* Primary Price */}
                    <div
                      className="font-display"
                      style={{
                        fontSize: 'clamp(2rem, 3.8vw, 2.75rem)',
                        fontWeight: 600,
                        color: '#FFFFFF',
                        lineHeight: 1.1,
                        marginBottom: '4px',
                      }}
                    >
                      {formatINRLakhCrore(result.estimated_price_inr)}
                    </div>

                    {/* Sub-rate per sq.ft. */}
                    <div style={{ fontSize: '0.875rem', color: '#94A3B8' }}>
                      ({formatPricePerSqFt(result.estimated_price_inr, result.area_value)})
                    </div>
                  </div>

                  {/* Building Thumbnail from Design Board */}
                  <div
                    style={{
                      position: 'relative',
                      width: '82px',
                      height: '68px',
                      borderRadius: 'var(--radius-xs)',
                      overflow: 'hidden',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      flexShrink: 0,
                    }}
                  >
                    <Image
                      src="/images/val-thumb.png"
                      alt="Property Valuation Showcase"
                      fill
                      sizes="82px"
                      style={{ objectFit: 'cover' }}
                    />
                  </div>
                </div>

                {/* Divider */}
                <div
                  style={{
                    height: '1px',
                    backgroundColor: 'rgba(255, 255, 255, 0.12)',
                    margin: '24px 0',
                  }}
                />

                {/* Specs Breakdown */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', marginBottom: '28px' }}>
                  {/* Property Type */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--color-gold)',
                        flexShrink: 0,
                      }}
                    >
                      <Home size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Property Type</div>
                      <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#FFFFFF' }}>
                        {result.furnishing || propertyType}
                      </div>
                    </div>
                  </div>

                  {/* Location */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--color-gold)',
                        flexShrink: 0,
                      }}
                    >
                      <MapPin size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Location</div>
                      <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#FFFFFF' }}>
                        {result.location}
                      </div>
                    </div>
                  </div>

                  {/* Area */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--color-gold)',
                        flexShrink: 0,
                      }}
                    >
                      <Maximize2 size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Area</div>
                      <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#FFFFFF' }}>
                        {result.area_value} sq.ft. ({result.area_basis})
                      </div>
                    </div>
                  </div>

                  {/* Bedrooms */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--color-gold)',
                        flexShrink: 0,
                      }}
                    >
                      <Bed size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Bedrooms</div>
                      <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#FFFFFF' }}>
                        {result.bhk ? `${result.bhk} BHK` : `${bhk || 2} BHK`}
                      </div>
                    </div>
                  </div>

                  {/* Bathrooms */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div
                      style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'var(--color-gold)',
                        flexShrink: 0,
                      }}
                    >
                      <Bath size={16} />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Bathrooms</div>
                      <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: '#FFFFFF' }}>
                        {result.bathrooms ?? bathrooms ?? 2}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Bottom Disclaimer & Audit ID */}
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    paddingTop: '20px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.12)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                    <BarChart2 size={16} color="var(--color-gold)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <div style={{ fontSize: '0.75rem', color: '#94A3B8', lineHeight: 1.5 }}>
                      Algorithmic estimate derived from continuous historical sales data. Intended for market research and guidance.
                    </div>
                  </div>
                  <div style={{ fontSize: '0.6875rem', color: '#64748B', fontFamily: 'monospace' }}>
                    ID: #{result.id.slice(0, 13)} • Saved to dashboard
                  </div>
                </div>
              </div>
            ) : (
              /* INITIAL NEUTRAL EMPTY STATE */
              <div style={{ padding: '12px 4px' }}>
                <span
                  style={{
                    display: 'inline-block',
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    color: 'var(--color-gold)',
                    marginBottom: '12px',
                  }}
                >
                  ESTIMATED VALUATION
                </span>

                <h3
                  className="font-display"
                  style={{
                    fontSize: 'clamp(1.5rem, 2.5vw, 1.875rem)',
                    fontWeight: 600,
                    color: '#FFFFFF',
                    lineHeight: 1.25,
                    marginBottom: '12px',
                  }}
                >
                  Your estimated property value will appear here.
                </h3>

                <p
                  style={{
                    fontSize: '0.9375rem',
                    color: '#CBD5E1',
                    lineHeight: 1.6,
                    marginBottom: '28px',
                  }}
                >
                  Enter the details on the left and click &quot;Get Valuation&quot; to calculate the estimated property price using our ML model.
                </p>

                {/* Live Parameters Preview */}
                <div
                  style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '20px',
                    marginBottom: '28px',
                  }}
                >
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-gold)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '14px' }}>
                    Configured Attributes
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', fontSize: '0.8125rem' }}>
                    <div>
                      <div style={{ color: '#94A3B8' }}>Micro-Market</div>
                      <div style={{ fontWeight: 600, color: '#FFFFFF', marginTop: '2px' }}>{location || 'Bangalore'}</div>
                    </div>
                    <div>
                      <div style={{ color: '#94A3B8' }}>Property Type</div>
                      <div style={{ fontWeight: 600, color: '#FFFFFF', marginTop: '2px' }}>{propertyType}</div>
                    </div>
                    <div>
                      <div style={{ color: '#94A3B8' }}>Area Basis</div>
                      <div style={{ fontWeight: 600, color: '#FFFFFF', marginTop: '2px' }}>{areaValue || 1150} sq.ft. ({areaBasis})</div>
                    </div>
                    <div>
                      <div style={{ color: '#94A3B8' }}>Configuration</div>
                      <div style={{ fontWeight: 600, color: '#FFFFFF', marginTop: '2px' }}>{bhk || 2} BHK / {bathrooms || 2} Bath</div>
                    </div>
                  </div>
                </div>

                {/* Model Info Note */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    paddingTop: '20px',
                    borderTop: '1px solid rgba(255, 255, 255, 0.12)',
                  }}
                >
                  <BarChart2 size={18} color="var(--color-gold)" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', lineHeight: 1.5 }}>
                    Engine: Tuned HistGradientBoostingRegressor • Holdout Test R² = 0.7104, MAE = ₹26.94L across 81 Indian micro-markets.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* BOTTOM BANNER: Why Choose GharScope? matching Design Board */}
        <div
          style={{
            backgroundColor: 'var(--color-primary-dark)',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            alignItems: 'center',
            boxShadow: 'var(--shadow-card)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {/* Left Text */}
          <div style={{ padding: '44px 40px' }}>
            <h2
              className="font-display"
              style={{
                fontSize: '1.75rem',
                fontWeight: 600,
                color: '#FFFFFF',
                marginBottom: '12px',
              }}
            >
              Why Choose GharScope?
            </h2>
            <p
              style={{
                color: '#CBD5E1',
                fontSize: '0.9375rem',
                lineHeight: 1.6,
                marginBottom: '24px',
                maxWidth: '460px',
              }}
            >
              Trusted by home buyers, property owners and real estate professionals for accurate, data-driven property valuations.
            </p>
            <Link
              href="/about"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                color: '#FFFFFF',
                fontSize: '0.9375rem',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              <span>Learn More</span>
              <ArrowRight size={16} />
            </Link>
          </div>

          {/* Right Terrace Image */}
          <div
            style={{
              position: 'relative',
              width: '100%',
              minHeight: '220px',
              height: '100%',
            }}
          >
            <Image
              src="/images/why-choose-terrace.png"
              alt="Luxury Living Penthouse Terrace"
              fill
              sizes="(max-width: 768px) 100vw, 500px"
              style={{ objectFit: 'cover', objectPosition: 'center' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
