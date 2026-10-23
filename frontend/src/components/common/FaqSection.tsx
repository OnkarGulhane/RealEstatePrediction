'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ChevronDown, MessageSquare, ArrowRight } from 'lucide-react';

interface FaqItem {
  id: string;
  question: string;
  answer: string;
}

const FAQS: FaqItem[] = [
  {
    id: 'faq-1',
    question: 'How does GharScope calculate property valuations?',
    answer:
      'GharScope uses a tuned HistGradientBoosting machine learning model trained on continuous historical asking prices across 81 Indian micro-markets. It evaluates 22 distinct parameters including normalized carpet/super area, layout (BHK/bathrooms), floor positioning, parking allocation (Treatment B logic), and micro-market locality demand to predict realistic market valuation tendencies.',
  },
  {
    id: 'faq-2',
    question: 'What is the difference between Carpet Area and Super Built-up Area?',
    answer:
      'Carpet Area is the net usable floor area inside the inner walls of your home where you can spread a carpet. Super Built-up Area (saleable area) includes the carpet area plus your proportionate share of common amenities (corridors, elevator shafts, clubhouse, staircases). GharScope explicitly normalizes both area bases to ensure you get accurate, un-inflated price-per-sq.ft. estimates.',
  },
  {
    id: 'faq-3',
    question: 'Does GharScope replace an official bank appraisal or legal title check?',
    answer:
      'No. GharScope estimates provide statistical market guidance, fair-value benchmarks, and transparent negotiation leverage. They reflect central statistical tendencies from verified market listings and do not constitute physical home inspections, chartered surveyor appraisals, or bank underwriting guarantees. Independent due diligence is always recommended.',
  },
  {
    id: 'faq-4',
    question: 'Which Indian cities and micro-markets are currently covered?',
    answer:
      'We currently cover 81 major residential micro-markets across Tier 1 and high-growth Tier 2 metropolitan regions, including Bangalore (Whitefield, Indiranagar, Electronic City, etc.), Mumbai (Andheri, Bandra, Powai, etc.), Pune (Baner, Wakad, Kharadi, etc.), Delhi NCR (Gurgaon, Noida, etc.), Hyderabad (Gachibowli, Hitec City, etc.), and Chennai (OMR, Anna Nagar, etc.).',
  },
  {
    id: 'faq-5',
    question: 'How do I save, compare, and track my property valuations over time?',
    answer:
      'By creating a free GharScope account, every property valuation you execute is permanently recorded in your private, encrypted User Dashboard. You can revisit past estimates, inspect detailed breakdown summaries, and track market changes across multiple properties.',
  },
];

export default function FaqSection() {
  const [openId, setOpenId] = useState<string | null>('faq-1');
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');

  const toggleFaq = (id: string) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  const handleFeedbackSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (feedbackText.trim()) {
      setFeedbackSent(true);
      setTimeout(() => {
        setFeedbackSent(false);
        setFeedbackText('');
      }, 2500);
    }
  };

  return (
    <section
      id="faq"
      style={{
        paddingTop: '72px',
        paddingBottom: '80px',
        backgroundColor: 'var(--color-ivory)',
        borderTop: '1px solid var(--color-border)',
        scrollMarginTop: 'var(--header-height)',
      }}
    >
      <div className="container-wide">
        {/* Section Header */}
        <div style={{ maxWidth: '640px', marginBottom: '48px' }}>
          <span
            className="eyebrow"
            style={{
              display: 'inline-block',
              marginBottom: '12px',
              color: 'var(--color-primary)',
              letterSpacing: '0.08em',
            }}
          >
            CLEAR ANSWERS &amp; TRANSPARENCY
          </span>
          <h2
            className="font-display"
            style={{
              fontSize: 'var(--text-h2)',
              fontWeight: 600,
              color: 'var(--color-dark)',
              lineHeight: 1.2,
              marginBottom: '14px',
            }}
          >
            Frequently Asked Questions
          </h2>
          <p
            style={{
              fontSize: '1rem',
              color: 'var(--text-secondary)',
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            Everything you need to know about our data-driven machine learning valuations, area standards, and market coverage.
          </p>
        </div>

        {/* 2-Column Layout: Accordion on Left (7fr), Feedback & Support Card on Right (4fr) */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: '40px',
            alignItems: 'flex-start',
          }}
        >
          {/* Left: Accordion List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {FAQS.map((faq) => {
              const isOpen = openId === faq.id;
              return (
                <div
                  key={faq.id}
                  className={`faq-accordion-item ${isOpen ? 'open' : ''}`}
                >
                  <button
                    type="button"
                    onClick={() => toggleFaq(faq.id)}
                    aria-expanded={isOpen}
                    style={{
                      width: '100%',
                      padding: '20px 24px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '16px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontFamily: 'var(--font-ui)',
                    }}
                  >
                    <span
                      style={{
                        fontSize: '1rem',
                        fontWeight: 600,
                        color: isOpen ? 'var(--color-primary)' : 'var(--color-dark)',
                        lineHeight: 1.4,
                      }}
                    >
                      {faq.question}
                    </span>
                    <div
                      className="faq-chevron-circle"
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        backgroundColor: isOpen ? 'rgba(15, 61, 54, 0.08)' : 'var(--color-surface-subtle)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: isOpen ? 'var(--color-primary)' : 'var(--text-muted)',
                        transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                        flexShrink: 0,
                      }}
                    >
                      <ChevronDown size={16} />
                    </div>
                  </button>

                  {isOpen && (
                    <div
                      style={{
                        padding: '0 24px 22px 24px',
                        fontSize: '0.9375rem',
                        color: 'var(--text-secondary)',
                        lineHeight: 1.65,
                        borderTop: '1px solid var(--color-border-subtle)',
                        paddingTop: '16px',
                      }}
                    >
                      {faq.answer}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Right: Feedback & User Support Card */}
          <div className="feedback-card">
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'rgba(15, 61, 54, 0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-primary)',
                marginBottom: '18px',
              }}
            >
              <MessageSquare size={22} strokeWidth={2.2} />
            </div>

            <h3
              className="font-display"
              style={{
                fontSize: '1.25rem',
                fontWeight: 600,
                color: 'var(--color-dark)',
                marginBottom: '10px',
                lineHeight: 1.3,
              }}
            >
              Have Feedback or a Locality Request?
            </h3>

            <p
              style={{
                fontSize: '0.875rem',
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
                marginBottom: '24px',
              }}
            >
              GharScope is built with an open, data-first mindset. If your micro-market is missing or you have suggestions on model accuracy, our engineering team reviews all community input.
            </p>

            {/* Quick Feedback Form directly inside Card */}
            {!feedbackSent ? (
              <form onSubmit={handleFeedbackSubmit}>
                <div style={{ marginBottom: '14px' }}>
                  <label
                    htmlFor="faq-feedback-input"
                    style={{
                      display: 'block',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                      marginBottom: '6px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                    }}
                  >
                    Your Feedback / Suggestion
                  </label>
                  <textarea
                    id="faq-feedback-input"
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                    placeholder="E.g., Please add Hinjewadi Phase 3 (Pune) or update parking estimates..."
                    required
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 14px',
                      fontSize: '0.875rem',
                      fontFamily: 'var(--font-ui)',
                      color: 'var(--color-dark)',
                      backgroundColor: 'var(--color-surface-subtle)',
                      border: '1px solid var(--color-border)',
                      borderRadius: 'var(--radius-sm)',
                      outline: 'none',
                      resize: 'vertical',
                      lineHeight: 1.5,
                      boxSizing: 'border-box',
                    }}
                  />
                </div>
                <button
                  type="submit"
                  className="btn-primary"
                  style={{
                    width: '100%',
                    height: '42px',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                  }}
                >
                  <span>Submit Feedback</span>
                  <ArrowRight size={15} />
                </button>
              </form>
            ) : (
              <div
                style={{
                  padding: '16px',
                  backgroundColor: '#F0FDF4',
                  border: '1px solid #86EFAC',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--color-success)',
                  fontSize: '0.875rem',
                  lineHeight: 1.5,
                  textAlign: 'center',
                }}
              >
                <strong>Thank you!</strong> Your feedback has been recorded and shared with our ML engineering team.
              </div>
            )}

            <div
              style={{
                marginTop: '20px',
                paddingTop: '16px',
                borderTop: '1px solid var(--color-border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.8125rem',
              }}
            >
              <span style={{ color: 'var(--text-muted)' }}>Need methodology details?</span>
              <Link
                href="/about"
                style={{
                  color: 'var(--color-primary)',
                  fontWeight: 600,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  textDecoration: 'none',
                }}
              >
                <span>Read ML Spec</span>
                <ArrowRight size={13} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
