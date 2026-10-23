'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, ArrowRight } from 'lucide-react';

export default function HeroSearch() {
  const router = useRouter();
  const [query, setQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/properties?search=${encodeURIComponent(query.trim())}`);
    } else {
      router.push('/properties');
    }
  };

  return (
    <form
      onSubmit={handleSearch}
      className="hero-search-box"
    >
      <Search size={18} color="var(--text-muted)" style={{ flexShrink: 0, marginRight: '12px' }} />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by location, city or property type"
        aria-label="Search by location, city or property type"
        style={{
          border: 'none',
          outline: 'none',
          backgroundColor: 'transparent',
          fontSize: '0.9375rem',
          color: 'var(--color-dark)',
          width: '100%',
          fontFamily: 'var(--font-ui)',
        }}
      />
      <button
        type="submit"
        className="btn-primary"
        style={{
          height: '42px',
          padding: '0 20px',
          borderRadius: 'var(--radius-xs)',
          fontSize: '0.875rem',
          fontWeight: 600,
          flexShrink: 0,
        }}
      >
        <span>Search</span>
        <ArrowRight size={15} />
      </button>
    </form>
  );
}
