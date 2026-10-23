/**
 * Indian Rupee (INR) and Date Formatters for GharScope
 * Follows official Indian numbering system (Lakhs & Crores)
 */

export function formatINRLakhCrore(amountInINR: number | null | undefined): string {
  if (amountInINR === null || amountInINR === undefined || isNaN(amountInINR)) {
    return '₹0';
  }

  const absAmount = Math.abs(amountInINR);

  if (absAmount >= 10_000_000) {
    const crores = amountInINR / 10_000_000;
    return `₹${crores.toFixed(2)} Cr`;
  }

  if (absAmount >= 100_000) {
    const lakhs = amountInINR / 100_000;
    return `₹${lakhs.toFixed(2)} L`;
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amountInINR);
}

export function formatINRExact(amountInINR: number | null | undefined): string {
  if (amountInINR === null || amountInINR === undefined || isNaN(amountInINR)) {
    return '₹0';
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amountInINR);
}

export function formatPricePerSqFt(priceInINR: number, areaSqFt: number): string {
  if (!areaSqFt || areaSqFt <= 0) {
    return '—';
  }
  const rate = Math.round(priceInINR / areaSqFt);
  return `₹${rate.toLocaleString('en-IN')}/sq.ft.`;
}

export function formatDateIST(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}
