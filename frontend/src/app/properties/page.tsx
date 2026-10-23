'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  Heart,
  ChevronDown,
  ArrowRight,
  LayoutGrid,
  List,
  RotateCcw,
} from 'lucide-react';

interface PropertyItem {
  id: string;
  image: string;
  city: string;
  neighborhood: string;
  type: string;
  areaSqFt: number;
  beds: number;
  priceDisplay: string;
  priceNumericInLakhs: number;
  statusBadge: string;
}

const BENCHMARK_PROPERTIES: PropertyItem[] = [
  {
    id: 'prop-1',
    image: '/images/properties/prop-bangalore.png',
    city: 'Bangalore',
    neighborhood: 'Whitefield, Bangalore',
    type: 'Apartment',
    areaSqFt: 1450,
    beds: 3,
    priceDisplay: '₹ 1.25 Cr',
    priceNumericInLakhs: 125,
    statusBadge: 'For Sale',
  },
  {
    id: 'prop-2',
    image: '/images/properties/prop-pune.png',
    city: 'Pune',
    neighborhood: 'Baner, Pune',
    type: 'Villa',
    areaSqFt: 2800,
    beds: 4,
    priceDisplay: '₹ 3.40 Cr',
    priceNumericInLakhs: 340,
    statusBadge: 'For Sale',
  },
  {
    id: 'prop-3',
    image: '/images/properties/prop-mumbai.png',
    city: 'Mumbai',
    neighborhood: 'Andheri West, Mumbai',
    type: 'Apartment',
    areaSqFt: 980,
    beds: 2,
    priceDisplay: '₹ 1.85 Cr',
    priceNumericInLakhs: 185,
    statusBadge: 'For Sale',
  },
  {
    id: 'prop-4',
    image: '/images/properties/prop-hyderabad.png',
    city: 'Hyderabad',
    neighborhood: 'Gachibowli, Hyderabad',
    type: 'Apartment',
    areaSqFt: 1650,
    beds: 3,
    priceDisplay: '₹ 1.10 Cr',
    priceNumericInLakhs: 110,
    statusBadge: 'For Sale',
  },
  {
    id: 'prop-5',
    image: '/images/properties/prop-gurgaon.png',
    city: 'Gurgaon',
    neighborhood: 'Gurgaon, Delhi NCR',
    type: 'Villa',
    areaSqFt: 3200,
    beds: 4,
    priceDisplay: '₹ 4.25 Cr',
    priceNumericInLakhs: 425,
    statusBadge: 'For Sale',
  },
  {
    id: 'prop-6',
    image: '/images/properties/prop-chennai.png',
    city: 'Chennai',
    neighborhood: 'OMR, Chennai',
    type: 'Apartment',
    areaSqFt: 1050,
    beds: 2,
    priceDisplay: '₹ 95 L',
    priceNumericInLakhs: 95,
    statusBadge: 'For Sale',
  },
];

export default function PropertiesPage() {
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedBudget, setSelectedBudget] = useState('');
  const [selectedBeds, setSelectedBeds] = useState('');
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const toggleFavorite = (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setFavorites((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const resetFilters = () => {
    setSelectedCity('');
    setSelectedType('');
    setSelectedBudget('');
    setSelectedBeds('');
  };

  const filteredProperties = useMemo(() => {
    return BENCHMARK_PROPERTIES.filter((p) => {
      if (selectedCity && p.city.toLowerCase() !== selectedCity.toLowerCase()) {
        return false;
      }
      if (selectedType && p.type.toLowerCase() !== selectedType.toLowerCase()) {
        return false;
      }
      if (selectedBeds && p.beds !== parseInt(selectedBeds, 10)) {
        return false;
      }
      if (selectedBudget) {
        if (selectedBudget === 'under-1cr' && p.priceNumericInLakhs >= 100) return false;
        if (selectedBudget === '1cr-2cr' && (p.priceNumericInLakhs < 100 || p.priceNumericInLakhs > 200)) return false;
        if (selectedBudget === '2cr-4cr' && (p.priceNumericInLakhs < 200 || p.priceNumericInLakhs > 400)) return false;
        if (selectedBudget === 'above-4cr' && p.priceNumericInLakhs < 400) return false;
      }
      return true;
    });
  }, [selectedCity, selectedType, selectedBudget, selectedBeds]);

  return (
    <div style={{ backgroundColor: 'var(--color-ivory)', minHeight: 'calc(100vh - var(--header-height))', paddingBottom: '80px' }}>
      <div className="container-wide" style={{ paddingTop: '32px' }}>
        
        {/* TOP HERO BANNER matching 2. Property Catalogue (Final Design) */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            minHeight: '160px',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            marginBottom: '32px',
            backgroundColor: 'var(--color-primary-dark)',
            display: 'flex',
            alignItems: 'center',
            boxShadow: 'var(--shadow-card)',
          }}
        >
          {/* Banner architectural photo on right */}
          <div
            style={{
              position: 'absolute',
              right: 0,
              top: 0,
              bottom: 0,
              width: '50%',
              minWidth: '320px',
              zIndex: 1,
            }}
          >
            <Image
              src="/images/properties/catalogue-photo.png"
              alt="Luxury modern apartments"
              fill
              sizes="(max-width: 768px) 100vw, 50vw"
              priority
              style={{ objectFit: 'cover', objectPosition: 'center' }}
            />
            {/* Gradient overlay for text readability */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background: 'linear-gradient(to right, var(--color-primary-dark) 0%, rgba(10, 38, 31, 0.4) 60%, transparent 100%)',
              }}
            />
          </div>

          {/* Left Text Content */}
          <div
            style={{
              position: 'relative',
              zIndex: 2,
              padding: '36px 40px',
              maxWidth: '640px',
            }}
          >
            <h1
              className="font-display"
              style={{
                fontSize: 'clamp(1.75rem, 3.2vw, 2.5rem)',
                fontWeight: 600,
                color: '#FFFFFF',
                lineHeight: 1.15,
                marginBottom: '12px',
              }}
            >
              Explore Premium Properties
            </h1>
            <p
              style={{
                fontSize: '0.9375rem',
                color: '#CBD5E1',
                lineHeight: 1.55,
                margin: 0,
              }}
            >
              Discover handpicked residential properties across India&apos;s top micro-markets. Find your perfect home or investment opportunity.
            </p>
          </div>
        </div>

        {/* HORIZONTAL SEARCH & FILTER BAR matching Final Design Board */}
        <div
          className="catalogue-filter-bar"
          style={{
            backgroundColor: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '16px 20px',
            marginBottom: '32px',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          {/* Location Select */}
          <div style={{ position: 'relative' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Location
            </label>
            <div style={{ position: 'relative' }}>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                style={{
                  width: '100%',
                  height: '42px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-surface)',
                  padding: '0 32px 0 12px',
                  fontSize: '0.875rem',
                  color: 'var(--color-dark)',
                  appearance: 'none',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                <option value="">All Locations</option>
                <option value="Bangalore">Bangalore</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Pune">Pune</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Gurgaon">Gurgaon</option>
                <option value="Chennai">Chennai</option>
              </select>
              <ChevronDown size={16} color="var(--text-secondary)" style={{ position: 'absolute', right: '12px', top: '13px', pointerEvents: 'none' }} />
            </div>
          </div>

          {/* Property Type Select */}
          <div style={{ position: 'relative' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Property Type
            </label>
            <div style={{ position: 'relative' }}>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                style={{
                  width: '100%',
                  height: '42px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-surface)',
                  padding: '0 32px 0 12px',
                  fontSize: '0.875rem',
                  color: 'var(--color-dark)',
                  appearance: 'none',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                <option value="">All Types</option>
                <option value="Apartment">Apartment</option>
                <option value="Villa">Villa</option>
              </select>
              <ChevronDown size={16} color="var(--text-secondary)" style={{ position: 'absolute', right: '12px', top: '13px', pointerEvents: 'none' }} />
            </div>
          </div>

          {/* Budget Range Select */}
          <div style={{ position: 'relative' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Budget Range
            </label>
            <div style={{ position: 'relative' }}>
              <select
                value={selectedBudget}
                onChange={(e) => setSelectedBudget(e.target.value)}
                style={{
                  width: '100%',
                  height: '42px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-surface)',
                  padding: '0 32px 0 12px',
                  fontSize: '0.875rem',
                  color: 'var(--color-dark)',
                  appearance: 'none',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                <option value="">All Budgets</option>
                <option value="under-1cr">Under ₹ 1 Cr</option>
                <option value="1cr-2cr">₹ 1 Cr - ₹ 2 Cr</option>
                <option value="2cr-4cr">₹ 2 Cr - ₹ 4 Cr</option>
                <option value="above-4cr">₹ 4 Cr+</option>
              </select>
              <ChevronDown size={16} color="var(--text-secondary)" style={{ position: 'absolute', right: '12px', top: '13px', pointerEvents: 'none' }} />
            </div>
          </div>

          {/* Bedrooms Select */}
          <div style={{ position: 'relative' }}>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
              Bedrooms
            </label>
            <div style={{ position: 'relative' }}>
              <select
                value={selectedBeds}
                onChange={(e) => setSelectedBeds(e.target.value)}
                style={{
                  width: '100%',
                  height: '42px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--color-border)',
                  backgroundColor: 'var(--color-surface)',
                  padding: '0 32px 0 12px',
                  fontSize: '0.875rem',
                  color: 'var(--color-dark)',
                  appearance: 'none',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                <option value="">Any</option>
                <option value="2">2 BHK</option>
                <option value="3">3 BHK</option>
                <option value="4">4 BHK</option>
              </select>
              <ChevronDown size={16} color="var(--text-secondary)" style={{ position: 'absolute', right: '12px', top: '13px', pointerEvents: 'none' }} />
            </div>
          </div>

          {/* Search / Reset Buttons */}
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
            <button
              onClick={resetFilters}
              className="btn-secondary"
              style={{ height: '42px', padding: '0 14px', borderRadius: 'var(--radius-xs)' }}
              title="Reset Filters"
            >
              <RotateCcw size={15} />
            </button>
            <button
              className="btn-primary"
              style={{
                height: '42px',
                padding: '0 24px',
                borderRadius: 'var(--radius-xs)',
                fontWeight: 600,
                fontSize: '0.875rem',
              }}
            >
              <span>Search</span>
            </button>
          </div>
        </div>

        {/* RESULTS HEADER & SORTING */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
          }}
        >
          <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-dark)' }}>
            Showing 1-{filteredProperties.length} of {filteredProperties.length} properties
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '10px', fontWeight: 400 }}>
              (Curated Showcase Properties)
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>Sort by:</span>
              <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>Recommended →</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <button
                onClick={() => setViewMode('grid')}
                style={{
                  background: viewMode === 'grid' ? 'var(--color-surface)' : 'transparent',
                  border: '1px solid var(--color-border)',
                  borderRadius: '4px',
                  padding: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  color: viewMode === 'grid' ? 'var(--color-primary)' : 'var(--text-muted)',
                }}
                aria-label="Grid View"
              >
                <LayoutGrid size={16} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                style={{
                  background: viewMode === 'list' ? 'var(--color-surface)' : 'transparent',
                  border: '1px solid var(--color-border)',
                  borderRadius: '4px',
                  padding: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  color: viewMode === 'list' ? 'var(--color-primary)' : 'var(--text-muted)',
                }}
                aria-label="List View"
              >
                <List size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* PROPERTY CARDS GRID matching Final Design Board */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '24px',
          }}
        >
          {filteredProperties.map((prop) => (
            <div
              key={prop.id}
              className="property-card"
            >
              {/* Card Photo with Status Badge & Favorite Heart */}
              <div
                style={{
                  position: 'relative',
                  width: '100%',
                  aspectRatio: '149 / 74',
                  backgroundColor: 'var(--color-surface-subtle)',
                }}
              >
                <Image
                  src={prop.image}
                  alt={`${prop.city} ${prop.type}`}
                  fill
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  style={{ objectFit: 'cover' }}
                />

                {/* Status Badge */}
                <div
                  style={{
                    position: 'absolute',
                    top: '12px',
                    left: '12px',
                    padding: '4px 10px',
                    backgroundColor: 'rgba(15, 61, 54, 0.88)',
                    backdropFilter: 'blur(4px)',
                    borderRadius: 'var(--radius-xs)',
                    color: '#FFFFFF',
                    fontSize: '0.6875rem',
                    fontWeight: 600,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    boxShadow: '0 2px 6px rgba(0, 0, 0, 0.2)',
                  }}
                >
                  {prop.statusBadge}
                </div>

                {/* Heart Button */}
                <button
                  onClick={(e) => toggleFavorite(prop.id, e)}
                  aria-label={`Save ${prop.city} property to favorites`}
                  style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    boxShadow: '0 2px 6px rgba(0, 0, 0, 0.15)',
                    color: favorites[prop.id] ? 'var(--color-error)' : 'var(--color-dark)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <Heart size={16} fill={favorites[prop.id] ? 'var(--color-error)' : 'none'} />
                </button>
              </div>

              {/* Card Content matching exact board layout */}
              <div style={{ padding: '20px 22px', display: 'flex', flexDirection: 'column', flex: 1 }}>
                {/* City Heading */}
                <h3
                  className="font-display"
                  style={{
                    fontSize: '1.25rem',
                    fontWeight: 600,
                    color: 'var(--color-dark)',
                    margin: '0 0 6px 0',
                  }}
                >
                  {prop.neighborhood.split(',')[0]}
                </h3>

                {/* Specs Line: 2 BHK | 1,150 sq.ft. | Apartment */}
                <div
                  style={{
                    fontSize: '0.8125rem',
                    color: 'var(--text-secondary)',
                    fontWeight: 500,
                    marginBottom: '16px',
                  }}
                >
                  {prop.beds} BHK &nbsp;|&nbsp; {prop.areaSqFt.toLocaleString('en-IN')} sq.ft. &nbsp;|&nbsp; {prop.type}
                </div>

                {/* Price & Location Row */}
                <div
                  style={{
                    marginTop: 'auto',
                    paddingTop: '16px',
                    borderTop: '1px solid var(--color-border-subtle)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-end',
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        color: 'var(--color-primary)',
                        marginBottom: '4px',
                      }}
                    >
                      {prop.priceDisplay}
                    </div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      {prop.neighborhood}
                    </div>
                  </div>

                  {/* Direct Link to ML Valuation Tool */}
                  <Link
                    href={`/predict?location=${encodeURIComponent(prop.city)}&bhk=${prop.beds}&area=${prop.areaSqFt}&type=${encodeURIComponent(prop.type)}`}
                    className="btn-secondary"
                    style={{
                      height: '36px',
                      padding: '0 14px',
                      borderRadius: 'var(--radius-xs)',
                      fontSize: '0.8125rem',
                      fontWeight: 600,
                      gap: '6px',
                      color: 'var(--color-primary)',
                      borderColor: 'rgba(15, 61, 54, 0.25)',
                      textDecoration: 'none',
                      flexShrink: 0,
                    }}
                    title={`Estimate ${prop.neighborhood} with GharScope ML Model`}
                  >
                    <span>Value Property</span>
                    <ArrowRight size={13} />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
