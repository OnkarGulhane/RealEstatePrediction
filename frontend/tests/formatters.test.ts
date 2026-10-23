import test from 'node:test';
import assert from 'node:assert';
import {
  formatINRLakhCrore,
  formatINRExact,
  formatPricePerSqFt,
  formatDateIST,
} from '../src/lib/formatters.ts';

test('formatINRLakhCrore formats Crores correctly', () => {
  const result = formatINRLakhCrore(12500000);
  assert.strictEqual(result, '₹1.25 Cr');
});

test('formatINRLakhCrore formats Lakhs correctly', () => {
  const result = formatINRLakhCrore(8550000);
  assert.strictEqual(result, '₹85.50 L');
});

test('formatINRLakhCrore handles zero and null gracefully', () => {
  assert.strictEqual(formatINRLakhCrore(0), '₹0');
  assert.strictEqual(formatINRLakhCrore(null), '₹0');
  assert.strictEqual(formatINRLakhCrore(undefined), '₹0');
});

test('formatINRExact formats with standard Indian currency symbol', () => {
  const result = formatINRExact(12500000);
  assert.ok(result.includes('1,25,00,000') || result.includes('12,500,000') || result.startsWith('₹'));
});

test('formatPricePerSqFt calculates unit price correctly', () => {
  const result = formatPricePerSqFt(12000000, 1200);
  assert.strictEqual(result, '₹10,000/sq.ft.');
});

test('formatPricePerSqFt handles zero area gracefully', () => {
  assert.strictEqual(formatPricePerSqFt(1000000, 0), '—');
});

test('formatDateIST handles valid dates and nulls', () => {
  assert.strictEqual(formatDateIST(null), '—');
  assert.strictEqual(formatDateIST(undefined), '—');
  const formatted = formatDateIST('2026-10-23T10:00:00Z');
  assert.ok(formatted.includes('2026') || formatted.includes('Oct'));
});
