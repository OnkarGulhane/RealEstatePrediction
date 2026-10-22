/**
 * Shared TypeScript types for Frontend
 */

export interface PropertyPredictionInput {
  location: string;
  area_value: number;
  area_basis: 'CARPET' | 'SUPER';
  bhk?: number;
  bathrooms?: number;
  balcony?: number;
  furnishing?: string;
}

export interface PredictionResult {
  prediction_id: string;
  estimated_price_inr: number;
  currency: string;
  model_version: string;
  disclaimer: string;
}
