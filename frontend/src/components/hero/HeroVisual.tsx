'use client';

import React from 'react';
import Image from 'next/image';

export default function HeroVisual() {
  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '620px',
        aspectRatio: '16 / 12',
        minHeight: '400px',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        boxShadow: '0 20px 48px rgba(15, 23, 42, 0.12)',
        border: '1px solid var(--color-border)',
        backgroundColor: 'var(--color-surface)',
      }}
    >
      <Image
        src="/images/hero-villa-luxury.jpg"
        alt="GharScope Modern Luxury Architectural Villa Terrace"
        fill
        priority
        unoptimized
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 620px"
        style={{
          objectFit: 'cover',
          objectPosition: 'center',
          imageRendering: '-webkit-optimize-contrast',
        }}
      />
    </div>
  );
}

