import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { TrendingUp, ShieldCheck, Target, MapPin, ArrowRight } from 'lucide-react';
import HeroVisual from '../components/hero/HeroVisual';
import HeroSearch from '../components/hero/HeroSearch';

export default function HomePage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {/* 1. HERO SECTION matching 1. Homepage (Final Design) */}
      <section
        style={{
          paddingTop: '64px',
          paddingBottom: '76px',
          backgroundColor: 'var(--color-ivory)',
        }}
      >
        <div
          className="container-wide"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
            gap: '56px',
            alignItems: 'center',
          }}
        >
          {/* Left Column: Hero Content */}
          <div style={{ maxWidth: '580px' }}>
            <span
              className="eyebrow"
              style={{
                display: 'inline-block',
                marginBottom: '16px',
                color: 'var(--color-primary)',
              }}
            >
              Real Estate Valuation & Discovery Platform
            </span>

            <h1
              className="font-display"
              style={{
                fontSize: 'var(--text-display-xl)',
                fontWeight: 600,
                color: 'var(--color-dark)',
                lineHeight: 1.08,
                letterSpacing: '-0.02em',
                marginBottom: '20px',
              }}
            >
              Know the Value.<br />
              Find Your Place.
            </h1>

            <p
              style={{
                fontSize: '1.0625rem',
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
                marginBottom: '28px',
              }}
            >
              Get transparent and statistically validated property price estimates across 81 major Indian micro-markets.
            </p>

            {/* Dual Action CTAs matching Senior Product Design brief */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                flexWrap: 'wrap',
                marginBottom: '28px',
              }}
            >
              <Link
                href="/predict"
                className="btn-primary"
                style={{
                  height: '46px',
                  padding: '0 24px',
                  fontSize: '0.9375rem',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  textDecoration: 'none',
                }}
              >
                <span>Start Valuation</span>
                <ArrowRight size={16} />
              </Link>
              <a
                href="#how-it-works"
                className="btn-secondary"
                style={{
                  height: '46px',
                  padding: '0 22px',
                  fontSize: '0.9375rem',
                  fontWeight: 500,
                  display: 'inline-flex',
                  alignItems: 'center',
                  textDecoration: 'none',
                }}
              >
                <span>Learn How It Works</span>
              </a>
            </div>

            {/* Hero Search Bar */}
            <HeroSearch />
          </div>

          {/* Right Column: Architectural Hero Penthouse Visual with Live Telemetry */}
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <HeroVisual />
          </div>
        </div>
      </section>

      {/* 2. TRUST PILLARS SECTION (4 Cards matching Final Design Board) */}
      <section
        style={{
          paddingTop: '56px',
          paddingBottom: '64px',
          backgroundColor: 'var(--color-surface)',
          borderTop: '1px solid var(--color-border)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <div className="container-wide">
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '24px',
            }}
          >
            {/* Card 1: Data Driven */}
            <div className="pillar-card" style={{ height: '100%' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: 'rgba(15, 61, 54, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <TrendingUp size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Data Driven
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Powered by real market data and advanced machine learning models.
              </p>
            </div>

            {/* Card 2: Secure */}
            <div className="pillar-card" style={{ height: '100%' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: 'rgba(15, 61, 54, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <ShieldCheck size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Secure
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Enterprise-grade security with JWT, HttpOnly cookies and CSRF protection.
              </p>
            </div>

            {/* Card 3: Accurate */}
            <div className="pillar-card" style={{ height: '100%' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: 'rgba(15, 61, 54, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <Target size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Accurate
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Statistically validated estimates with proven offline holdout performance (Holdout R² = 0.7104, MAE = ₹26.94L).
              </p>
            </div>

            {/* Card 4: Pan India */}
            <div className="pillar-card" style={{ height: '100%' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: 'rgba(15, 61, 54, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <MapPin size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Pan India
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Coverage across 81 major Indian micro-markets.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS (Dark Forest Panel matching Final Design Board) */}
      <section
        id="how-it-works"
        style={{
          paddingTop: '80px',
          paddingBottom: '80px',
          backgroundColor: 'var(--color-primary-dark)',
          color: 'var(--text-on-dark)',
          scrollMarginTop: 'var(--header-height)',
        }}
      >
        <div className="container-wide">
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '280px 1fr',
              gap: '56px',
              alignItems: 'center',
            }}
            className="how-it-works-layout"
          >
            {/* Left Story Column */}
            <div>
              <span
                className="eyebrow"
                style={{
                  display: 'inline-block',
                  marginBottom: '12px',
                  color: 'var(--color-gold)',
                  letterSpacing: '0.08em',
                }}
              >
                SIMPLE 4-STEP PROCESS
              </span>
              <h2
                className="font-display"
                style={{
                  fontSize: 'var(--text-h2)',
                  fontWeight: 600,
                  color: '#FFFFFF',
                  lineHeight: 1.2,
                  marginBottom: '16px',
                }}
              >
                How It Works
              </h2>
              <p
                style={{
                  fontSize: '0.9375rem',
                  color: '#CBD5E1',
                  lineHeight: 1.6,
                  marginBottom: '28px',
                }}
              >
                Get accurate property valuations in just a few simple steps.
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

            {/* Right 4 Numbered Steps Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '20px',
              }}
            >
              {/* Step 01 */}
              <div className="step-card">
                <div
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    color: 'var(--color-gold)',
                    fontFamily: 'var(--font-mono)',
                    marginBottom: '12px',
                  }}
                >
                  01
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                  Enter Property Details
                </h3>
                <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
                  Provide location, property type and key features.
                </p>
              </div>

              {/* Step 02 */}
              <div className="step-card">
                <div
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    color: 'var(--color-gold)',
                    fontFamily: 'var(--font-mono)',
                    marginBottom: '12px',
                  }}
                >
                  02
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                  Get Valuation
                </h3>
                <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
                  Our ML model analyzes market data and predicts value.
                </p>
              </div>

              {/* Step 03 */}
              <div className="step-card">
                <div
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    color: 'var(--color-gold)',
                    fontFamily: 'var(--font-mono)',
                    marginBottom: '12px',
                  }}
                >
                  03
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                  Explore Properties
                </h3>
                <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
                  Discover properties based on valuation and preferences.
                </p>
              </div>

              {/* Step 04 */}
              <div className="step-card">
                <div
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 700,
                    color: 'var(--color-gold)',
                    fontFamily: 'var(--font-mono)',
                    marginBottom: '12px',
                  }}
                >
                  04
                </div>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                  Make Confident Decisions
                </h3>
                <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.5, margin: 0 }}>
                  Buy, sell or invest with trusted insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. SMARTER DECISIONS BANNER (Matching Product Brief & Design Reference) */}
      <section
        style={{
          paddingTop: '64px',
          paddingBottom: '64px',
          backgroundColor: 'var(--color-ivory)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <div className="container-wide">
          <div
            style={{
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              alignItems: 'center',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            {/* Left Content */}
            <div style={{ padding: '48px 40px', maxWidth: '560px' }}>
              <span
                className="eyebrow"
                style={{
                  display: 'inline-block',
                  marginBottom: '12px',
                  color: 'var(--color-primary)',
                  letterSpacing: '0.08em',
                }}
              >
                SMARTER REAL ESTATE
              </span>
              <h2
                className="font-display"
                style={{
                  fontSize: 'var(--text-h2)',
                  fontWeight: 600,
                  color: 'var(--color-dark)',
                  lineHeight: 1.2,
                  marginBottom: '16px',
                }}
              >
                Smarter Decisions.<br />
                Greater Confidence.
              </h2>
              <p
                style={{
                  fontSize: '1rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.65,
                  marginBottom: '28px',
                }}
              >
                Whether evaluating a primary residence, acquiring an investment in Bangalore, or negotiating in Mumbai, GharScope brings statistical clarity to complex real estate decisions.
              </p>
              <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
                <Link
                  href="/predict"
                  className="btn-primary"
                  style={{
                    height: '46px',
                    padding: '0 24px',
                    fontSize: '0.9375rem',
                    fontWeight: 600,
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <span>Start Free Valuation</span>
                  <ArrowRight size={16} />
                </Link>
                <Link
                  href="/properties"
                  className="btn-secondary"
                  style={{
                    height: '46px',
                    padding: '0 22px',
                    fontSize: '0.9375rem',
                    fontWeight: 500,
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                  }}
                >
                  <span>Explore Properties</span>
                </Link>
              </div>
            </div>

            {/* Right Architectural Image */}
            <div
              style={{
                position: 'relative',
                height: '100%',
                minHeight: '340px',
                width: '100%',
              }}
            >
              <Image
                src="/images/smart-decisions-villa.png"
                alt="Modern luxury cantilever villa representing confident real estate investments"
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                style={{ objectFit: 'cover', objectPosition: 'center' }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 5. STATISTICAL VALUATION NOTICE FOOTER BANNER */}
      <section
        style={{
          paddingTop: '40px',
          paddingBottom: '48px',
          backgroundColor: 'var(--color-ivory)',
        }}
      >
        <div className="container-wide">
          <div
            style={{
              padding: '20px 24px',
              backgroundColor: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '16px',
            }}
          >
            <div style={{ maxWidth: '820px' }}>
              <span style={{ fontWeight: 600, color: 'var(--color-dark)', fontSize: '0.875rem' }}>
                Statistical Valuation Notice:{' '}
              </span>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                GharScope valuations are generated using an offline-validated Machine Learning model (Holdout Test R² = 0.7104, MAE = ₹26.94L) trained on verified Indian market listings. Estimates are intended for market guidance and do not constitute certified bank appraisals.
              </span>
            </div>
            <Link
              href="/about"
              className="btn-secondary"
              style={{ height: '36px', padding: '0 16px', fontSize: '0.8125rem' }}
            >
              <span>Model Methodology</span>
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
