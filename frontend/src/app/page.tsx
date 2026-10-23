import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { TrendingUp, ShieldCheck, Target, MapPin, ArrowRight } from 'lucide-react';
import HeroVisual from '../components/hero/HeroVisual';
import HeroSearch from '../components/hero/HeroSearch';
import FaqSection from '../components/common/FaqSection';

export default function HomePage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {/* 1. HERO SECTION matching Product Requirements & Approved Visual Concept */}
      <section
        style={{
          paddingTop: '64px',
          paddingBottom: '76px',
          backgroundColor: 'var(--color-ivory)',
        }}
      >
        <div className="container-wide">
          <div className="hero-grid">
            {/* Left Column: Hero Editorial Content */}
            <div style={{ maxWidth: '600px' }}>
              <span
                className="eyebrow"
                style={{
                  display: 'inline-block',
                  marginBottom: '16px',
                  color: 'var(--color-primary)',
                }}
              >
                Real Estate Valuation Platform
              </span>

              <h1
                className="font-display"
                style={{
                  fontSize: 'var(--text-display-xl)',
                  fontWeight: 600,
                  color: 'var(--color-dark)',
                  lineHeight: 1.1,
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
                  marginBottom: '32px',
                  maxWidth: '520px',
                }}
              >
                Get accurate, data-driven property price estimates across India&apos;s 81 key micro-markets.
              </p>

              {/* Dual Action CTAs strictly matching Requirements without Video Gimmicks */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  flexWrap: 'wrap',
                  marginBottom: '32px',
                }}
              >
                <Link
                  href="/predict"
                  className="btn-primary"
                  style={{
                    height: '48px',
                    padding: '0 26px',
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
                    height: '48px',
                    padding: '0 24px',
                    fontSize: '0.9375rem',
                    fontWeight: 600,
                    display: 'inline-flex',
                    alignItems: 'center',
                    textDecoration: 'none',
                  }}
                >
                  <span>Learn How It Works</span>
                </a>
              </div>

              {/* Subordinate Functional Property Search Bar routing to Catalogue */}
              <div style={{ maxWidth: '480px' }}>
                <HeroSearch />
              </div>
            </div>

            {/* Right Column: Prominent Architectural Hero Visual with 2 Metric Cards */}
            <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
              <HeroVisual />
            </div>
          </div>
        </div>
      </section>

      {/* 2. WHY GHARSCOPE? (Full-Width Composition with 4 Horizontally Aligned Cards on Desktop) */}
      <section
        style={{
          paddingTop: '80px',
          paddingBottom: '88px',
          backgroundColor: 'var(--color-ivory)',
          borderTop: '1px solid var(--color-border-subtle)',
          borderBottom: '1px solid var(--color-border-subtle)',
        }}
      >
        <div className="container-wide">
          {/* Section Header Area: Compact & Well-Aligned */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
              alignItems: 'flex-end',
              gap: '24px',
              marginBottom: '40px',
            }}
          >
            <div style={{ maxWidth: '640px' }}>
              <span
                className="eyebrow"
                style={{
                  display: 'inline-block',
                  marginBottom: '10px',
                  color: 'var(--color-primary)',
                  letterSpacing: '0.08em',
                }}
              >
                PLATFORM CAPABILITIES
              </span>
              <h2
                className="font-display"
                style={{
                  fontSize: 'var(--text-h2)',
                  fontWeight: 600,
                  color: 'var(--color-dark)',
                  lineHeight: 1.2,
                  marginBottom: '12px',
                }}
              >
                Why GharScope?
              </h2>
              <p
                style={{
                  fontSize: '1rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.6,
                  margin: 0,
                }}
              >
                Built on real market data. Designed for smarter decisions. GharScope provides transparent, statistically validated property valuations &mdash; no guesswork, no inflated numbers.
              </p>
            </div>

            <div>
              <Link
                href="/about"
                className="btn-text-link"
                style={{
                  padding: '8px 0',
                }}
              >
                <span>Our Approach</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>

          {/* Four Feature Cards in ONE Single Horizontal Row on Desktop */}
          <div className="why-cards-row">
            {/* Card 1 — Data Driven */}
            <div className="why-feature-card">
              <div className="why-icon-circle">
                <TrendingUp size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.1875rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Data Driven
              </h3>
              <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Powered by real market data and machine-learning models.
              </p>
            </div>

            {/* Card 2 — Secure */}
            <div className="why-feature-card">
              <div className="why-icon-circle">
                <ShieldCheck size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.1875rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Secure
              </h3>
              <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Designed with protected authentication and privacy-conscious data handling.
              </p>
            </div>

            {/* Card 3 — Accurate */}
            <div className="why-feature-card">
              <div className="why-icon-circle">
                <Target size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.1875rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Accurate
              </h3>
              <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Statistically evaluated estimates backed by offline model testing.
              </p>
            </div>

            {/* Card 4 — Pan India */}
            <div className="why-feature-card">
              <div className="why-icon-circle">
                <MapPin size={22} strokeWidth={2.2} />
              </div>
              <h3 style={{ fontSize: '1.1875rem', fontWeight: 700, color: 'var(--color-dark)', margin: 0 }}>
                Pan India
              </h3>
              <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                Coverage across 81 major Indian micro-markets.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS (Full-Width Obsidian Forest Panel with Static Architectural Photography — No Fake Video Gimmicks) */}
      <section
        id="how-it-works"
        style={{
          paddingTop: '88px',
          paddingBottom: '92px',
          backgroundColor: 'var(--color-primary-dark)',
          color: 'var(--text-on-dark)',
          scrollMarginTop: 'var(--header-height)',
        }}
      >
        <div className="container-wide">
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
              gap: '56px',
              alignItems: 'center',
            }}
          >
            {/* Left Architectural Balcony Visual (Static Photography — No Play Buttons or Fake Player Controls) */}
            <div
              style={{
                position: 'relative',
                width: '100%',
                maxWidth: '480px',
                aspectRatio: '4 / 3',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
                boxShadow: '0 20px 48px rgba(0, 0, 0, 0.35)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
              }}
            >
              <Image
                src="/images/how-it-works-clean.jpg"
                alt="Modern High-Rise Residential Balcony Architecture"
                fill
                sizes="(max-width: 768px) 100vw, 480px"
                style={{ objectFit: 'cover', objectPosition: 'center' }}
              />
            </div>

            {/* Right: Eyebrow, H2, and Exactly 3 Numbered Steps */}
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
                HOW IT WORKS
              </span>
              <h2
                className="font-display"
                style={{
                  fontSize: 'var(--text-h2)',
                  fontWeight: 600,
                  color: '#FFFFFF',
                  lineHeight: 1.2,
                  marginBottom: '36px',
                }}
              >
                Get Your Property Valuation in 3 Simple Steps
              </h2>

              {/* Exactly 3 Numbered Steps Grid */}
              <div className="steps-3-grid">
                {/* Step 01 */}
                <div className="step-card">
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1.5px solid var(--color-gold)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--color-gold)',
                      fontFamily: 'var(--font-mono)',
                      marginBottom: '14px',
                    }}
                  >
                    01
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                    Enter Property Details
                  </h3>
                  <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.55, margin: 0 }}>
                    Add location, property type, size and more.
                  </p>
                </div>

                {/* Step 02 */}
                <div className="step-card">
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1.5px solid var(--color-gold)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--color-gold)',
                      fontFamily: 'var(--font-mono)',
                      marginBottom: '14px',
                    }}
                  >
                    02
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                    Review Estimate
                  </h3>
                  <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.55, margin: 0 }}>
                    Get a data-driven value based on our ML model.
                  </p>
                </div>

                {/* Step 03 */}
                <div className="step-card">
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1.5px solid var(--color-gold)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: 'var(--color-gold)',
                      fontFamily: 'var(--font-mono)',
                      marginBottom: '14px',
                    }}
                  >
                    03
                  </div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px', margin: '0 0 8px 0' }}>
                    Track History
                  </h3>
                  <p style={{ fontSize: '0.8125rem', color: '#94A3B8', lineHeight: 1.55, margin: 0 }}>
                    View and manage your past valuations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. SMARTER DECISIONS BANNER */}
      <section
        style={{
          paddingTop: '80px',
          paddingBottom: '80px',
          backgroundColor: 'var(--color-ivory)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        <div className="container-wide">
          <div className="smarter-banner-card">
            {/* Left Content */}
            <div style={{ padding: '56px 48px', maxWidth: '580px' }}>
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
                  marginBottom: '32px',
                }}
              >
                Whether you&apos;re buying, selling or just exploring &mdash; GharScope helps you make informed decisions with reliable property insights.
              </p>
              <div>
                <Link
                  href="/predict"
                  className="btn-primary"
                  style={{
                    height: '48px',
                    padding: '0 26px',
                    fontSize: '0.9375rem',
                    fontWeight: 600,
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                  }}
                >
                  <span>Get Started</span>
                  <ArrowRight size={16} />
                </Link>
              </div>
            </div>

            {/* Right Architectural Image */}
            <div
              style={{
                position: 'relative',
                height: '100%',
                minHeight: '380px',
                width: '100%',
              }}
            >
              <Image
                src="/images/smart-decisions-villa-clean.jpg"
                alt="Modern luxury cantilever villa representing confident real estate investments"
                fill
                sizes="(max-width: 768px) 100vw, 50vw"
                style={{ objectFit: 'cover', objectPosition: 'center' }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 5. FREQUENTLY ASKED QUESTIONS & COMMUNITY FEEDBACK */}
      <FaqSection />

      {/* 6. STATISTICAL VALUATION NOTICE FOOTER BANNER */}
      <section
        style={{
          paddingTop: '28px',
          paddingBottom: '36px',
          backgroundColor: 'var(--color-ivory)',
        }}
      >
        <div className="container-wide">
          <div className="stat-notice-card">
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
