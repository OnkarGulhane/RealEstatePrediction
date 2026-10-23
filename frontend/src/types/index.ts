/**
 * GharScope Shared TypeScript Domain & API Types
 * Strictly aligned with contracts/application-api.yaml
 */

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  is_staff: boolean;
  is_active: boolean;
  created_at: string;
}

export interface AuthSuccessResponse {
  user: UserProfile;
  access: string;
  token_type: string;
  expires_in: number;
}

export interface TokenRefreshResponse {
  access: string;
  token_type: string;
  expires_in: number;
}

export interface LocationItem {
  name: string;
  normalized: string;
}

export interface CategoriesMetadata {
  furnishing?: string[];
  transaction_type?: string[];
  status?: string[];
  facing?: string[];
  ownership?: string[];
}

export interface LocationsMetadataResponse {
  schema_version: string;
  total_locations: number;
  locations: LocationItem[];
  area_bases: string[];
  categories: CategoriesMetadata;
}

export interface PropertyPredictionInput {
  schema_version: '1.0';
  location: string;
  area_value: number;
  area_basis: 'CARPET' | 'SUPER';
  bhk?: number | null;
  bathrooms?: number | null;
  balcony?: number | null;
  floor_number?: number | null;
  total_floors?: number | null;
  parking_spaces?: number | null;
  furnishing?: string | null;
  transaction_type?: string | null;
  status?: string | null;
  facing?: string | null;
  ownership?: string | null;
}

export interface PredictionRecord {
  id: string;
  user_id: string;
  location: string;
  area_value: number;
  area_basis: string;
  bhk: number | null;
  bathrooms: number | null;
  balcony: number | null;
  floor_number: number | null;
  total_floors: number | null;
  parking_spaces: number | null;
  furnishing: string | null;
  transaction_type: string | null;
  status: string | null;
  facing: string | null;
  ownership: string | null;
  estimated_price_inr: number;
  currency: string;
  model_version: string;
  schema_version: string;
  disclaimer?: string;
  created_at: string;
}

export interface PaginatedPredictionList {
  count: number;
  next: string | null;
  previous: string | null;
  results: PredictionRecord[];
}

export interface AdminSummaryResponse {
  users: {
    total: number;
    active: number;
    staff: number;
  };
  predictions: {
    total: number;
    total_volume_inr: number;
    average_price_inr: number;
    last_24_hours: number;
    last_7_days: number;
  };
  currency: string;
  server_time: string;
}

export interface AdminModelMetadataResponse {
  model_id: string;
  algorithm: string;
  test_evaluation: {
    r2_score: number;
    mae_inr: number;
    rmse_inr: number;
    median_absolute_error_inr: number;
    features_count: number;
  };
  disclaimer: string;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    fields?: Record<string, string[]>;
    request_id?: string;
  };
}
