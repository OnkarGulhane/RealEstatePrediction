'use client';

import React from 'react';
import Image from 'next/image';
import { MapPin } from 'lucide-react';

export default function HeroVisual() {
  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '680px',
        aspectRatio: '575 / 299',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        boxShadow: '0 20px 50px rgba(15, 23, 42, 0.12)',
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)',
      }}
    >
      <Image
        src="/images/hero-penthouse.png"
        alt="GharScope Modern Living Luxury Terrace Overlooking City Skyline"
        fill
        sizes="(max-width: 768px) 100vw, 680px"
        priority
        style={{
          objectFit: 'cover',
          objectPosition: 'center',
        }}
      />
      
      {/* Floating telemetry chip 1: Top Left */}
      <div
        style={{
          position: 'absolute',
          top: '18px',
          left: '18px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'rgba(255, 255, 255, 0.94)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          padding: '6px 14px',
          borderRadius: 'var(--radius-pill)',
          boxShadow: '0 4px 14px rgba(15, 23, 42, 0.12)',
          border: '1px solid rgba(226, 232, 240, 0.9)',
          zIndex: 3,
        }}
      >
        <MapPin size={13} color="var(--color-primary)" />
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-dark)', letterSpacing: '0.01em' }}>
          81 Indian Micro-Markets
        </span>
      </div>

      {/* Subtle bottom gradient to make overlay text pop */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(15, 23, 42, 0.65) 0%, rgba(15, 23, 42, 0.15) 45%, transparent 75%)',
          pointerEvents: 'none',
        }}
      />

      {/* Floating telemetry chip 2: Bottom Left */}
      <div
        style={{
          position: 'absolute',
          bottom: '22px',
          left: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'rgba(10, 38, 31, 0.88)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          padding: '6px 14px',
          borderRadius: 'var(--radius-pill)',
          border: '1px solid rgba(212, 175, 55, 0.4)',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)',
          zIndex: 3,
        }}
      >
        <span
          style={{
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            backgroundColor: 'var(--color-gold)',
            display: 'inline-block',
          }}
        />
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#FFFFFF', letterSpacing: '0.02em' }}>
          Holdout R² 0.7104 &bull; ₹26.94L MAE
        </span>
      </div>

      {/* Editorial Overlay Text matching Option A Design Board */}
      <div
        style={{
          position: 'absolute',
          bottom: '22px',
          right: '24px',
          textAlign: 'right',
          color: '#FFFFFF',
          zIndex: 2,
          pointerEvents: 'none',
        }}
      >
        <div
          style={{
            fontSize: '1rem',
            fontWeight: 500,
            letterSpacing: '-0.01em',
            marginBottom: '3px',
            fontFamily: 'var(--font-display)',
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.6)',
          }}
        >
          Modern living, better decisions.
        </div>
        <div
          style={{
            fontSize: '0.75rem',
            fontWeight: 600,
            color: 'rgba(255, 255, 255, 0.85)',
            letterSpacing: '0.04em',
            textShadow: '0 1px 6px rgba(0, 0, 0, 0.6)',
          }}
        >
          Trusted. Transparent. GharScope.
        </div>
      </div>
    </div>
  );
}
