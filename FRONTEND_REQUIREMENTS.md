# GharScope — Frontend Requirements Specification & Implementation Roadmap

> **Product:** GharScope (Real Estate Price Prediction Platform — India)  
> **Tagline:** *"Know the Value. Find Your Place."*  
> **Repository:** `OnkarGulhane/RealEstatePrediction`  
> **Target Phase:** Phase 5 — Next.js Frontend  
> **Document Status:** Authoritative Requirements & Architectural Specification (Stripped of AI-Slop & Unnecessary Bloat)  
> **Design Reference:** `DesignReference/GharScope Real Estate Design System.png` & `DesignReference/GharScope_Design_Tokens.md`  

---

## 1. Executive Summary & Product Mission

GharScope is a refined, trustworthy, data-driven residential real estate valuation and property discovery platform designed for Indian home buyers, property owners, and real estate professionals.

### Primary Purpose:
Provide **transparent, statistically validated residential property price estimates** across 81 major Indian micro-markets powered by the approved machine learning inference service and the Django REST application backend.

### Core Design & Engineering Principles:
1. **Art-Directed Luxury Aesthetics:** Strictly follow the approved human-crafted design system (`DesignReference/GharScope Real Estate Design System.png`). Deep forest greens, warm ivory surfaces, gold accents, and serif headings (`Playfair Display`).
2. **Zero AI-Slop & Zero Unnecessary Bloat:** **NO** 3D WebGL/Three.js or CSS 3D cubes, **NO** Lenis smooth-scroll bloat, **NO** heavy GSAP animation engines, **NO** neon gradients or fake counters. Every visual is high-resolution architectural photography or clean semantic SVG icons.
3. **Absolute Data Integrity:** Never fabricate mock listings, fake partner logos, or fake accuracy numbers. All reported metrics reflect real offline holdout evaluation ($R^2 = 0.7104$, $\text{MAE} = ₹26.94\text{L}$, $\text{RMSE} = ₹85.18\text{L}$).
4. **Enterprise Security & Token Safety:** In-memory JWT access token management, HttpOnly refresh cookies, strict CSRF token bootstrap, and zero credential leakage to `localStorage` or URL query params.
5. **Contract-Backed API Integration:** Bounded retry logic, single-flight refresh promises, and graceful handling of 401, 403, 503, and 504 server states strictly matching `contracts/application-api.yaml`.

---

## 2. Monorepo Architecture & Service Boundaries

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          GHARSCOPE SYSTEM TOPOLOGY                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   🌐 FRONTEND (Port 3000)                                                              │
│      - Framework: Next.js 16.x (App Router) + React 19 + TypeScript 5.x                │
│      - Styling: Vanilla CSS Tokens (GharScope Luxury Palette & Typographic Hierarchy)  │
│      - Assets: High-resolution architectural photography & Lucide icons                │
│      - Security: In-Memory Access JWT + CSRF Handshake                                 │
│                                                                                        │
│                         │ REST HTTP Calls ONLY (Never calls FastAPI directly)          │
│                         │ Cookie: refresh_token (HttpOnly, SameSite=Lax)               │
│                         │ Headers: Authorization: Bearer <token>, X-CSRFToken          │
│                         ▼                                                              │
│                                                                                        │
│   ⚙️ APPLICATION BACKEND (Port 8000)                                                    │
│      - Framework: Django 5.2 LTS + Django REST Framework                               │
│      - Base URL: http://localhost:8000/api/v1                                          │
│      - Responsibilities: Auth, User Management, History Persistence, Locations, Admin  │
│                                                                                        │
│                         │ Internal Microservice HTTP (Port 8001)                       │
│                         │ Header: X-Service-Token (Bearer Token)                       │
│                         │ Bounded Timeout: 3.0s | Max Retries: 2                       │
│                         ▼                                                              │
│                                                                                        │
│   🤖 INFERENCE MICROSERVICE (Port 8001)                                                │
│      - Framework: FastAPI 0.115                                                        │
│      - Model: HistGradientBoostingRegressor / LightGBM pipeline                        │
│      - Contract: Strict Phase 3 Schema (22 Features, Treatment B Parking Logic)        │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Strict Non-Negotiable Boundaries:
- **No Direct Inference Calls:** The browser must **never** call `http://127.0.0.1:8001` directly. All valuation submissions route through Django's `POST /api/v1/predictions/`.
- **Zero Backend/Contract Drift:** The frontend must conform strictly to `contracts/application-api.yaml`.
- **Lightweight Dependencies:** Keep bundle size minimal. Rely on native CSS transitions and standard browser capabilities.

---

## 3. Technology Stack & Essential Dependencies

| Category | Recommended Technology | Pinned / Compatible Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | `16.4.2` | Core SSR/SSG application framework |
| **Language** | TypeScript | `^5.7.2` | Static typing and contract schema alignment |
| **Runtime UI** | React / React-DOM | `^19.0.0` | Component composition and hooks |
| **Styling** | Vanilla CSS + CSS Variables | Native | Zero-runtime design tokens, complete control, fast |
| **Icons** | Lucide React | `^1.61.0` | Clean, accessible UI iconography matching design board |
| **Testing** | Node.js Test Runner | Native (`--experimental-strip-types`) | Fast, zero-dependency unit and integration testing |
| **Linting** | ESLint & Next.js config | `^9.20.0` / `16.4.2` | Code quality and accessibility enforcement |

> **Note on Removed Libraries:** GSAP, `@gsap/react`, Three.js, and Lenis smooth-scroll have been intentionally excluded. Standard CSS transitions and native browser scrolling provide 60 FPS performance without bundle bloat.

---

## 4. Visual Identity & Design System (from Design Reference)

### 4.1 Exact Color Palette Tokens (`globals.css`)
```css
:root {
  /* Brand Colors from Design System */
  --color-primary: #0F3D36;          /* Deep Forest Green - Primary Buttons & Accents */
  --color-primary-dark: #0A261F;     /* Obsidian Forest - How It Works Banner */
  --color-secondary: #1F5D52;        /* Secondary Green - Hover States & Badges */
  --color-gold: #D4AF37;             /* Accent Gold - Premium Highlights */
  
  /* Canvas & Surface Colors */
  --color-ivory: #F8F6F1;            /* Warm Ivory - Page Background */
  --color-surface: #FFFFFF;          /* Pure White - Card & Container Surfaces */
  --color-surface-subtle: #F1F5F9;   /* Off-White - Subtle Input Backgrounds */
  --color-border: #E2E8F0;           /* Clean Border */
  --color-border-subtle: #EDEAE2;    /* Warm Divider */
  
  /* Typography Colors */
  --color-dark: #0F172A;             /* Slate 900 - Text Primary */
  --text-secondary: #64748B;         /* Slate 500 - Text Secondary / Body */
  --text-muted: #94A3B8;             /* Slate 400 - Muted Captions */
  --text-on-dark: #FFFFFF;           /* White text on Forest Green surfaces */
  
  /* System States */
  --color-error: #DC2626;            /* Error */
  --color-success: #16A34A;          /* Success */
  --color-warning: #D97706;          /* Warning */
}
```

### 4.2 Typography Hierarchy
- **Display Headings:** `Playfair Display`, Georgia, serif (weights: 500, 600, 700).
- **Body & UI Elements:** `Inter`, -apple-system, system-ui, sans-serif (weights: 400, 500, 600).
- **Scale:**
  - Display / Hero Headline: `clamp(2.75rem, 5vw, 4.25rem)` (line-height: 1.08)
  - Section Headings (`h2`): `clamp(1.85rem, 3vw, 2.75rem)` (line-height: 1.2)
  - Subheadings (`h3`): `1.25rem` to `1.5rem`
  - Body Text: `1rem` (line-height: 1.6)
  - Micro / Badges: `0.75rem` to `0.875rem`

---

## 5. Backend API Endpoints & Contract Specifications

All requests target base URL `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000/api/v1`).

### 5.1 Endpoint Inventory

| Endpoint | Method | Auth Required | Description & Contract Behavior |
| :--- | :--- | :--- | :--- |
| `/health/` | `GET` | No | Service liveness probe returning `{ status: "ok", service, version }`. |
| `/auth/csrf/` | `GET` | No (Cookie) | CSRF bootstrap: sets `csrftoken` cookie and returns `{ csrf_token }`. |
| `/auth/register/` | `POST` | No | Registers user (`email`, `password` $\ge 8$, `display_name`). Redirects to `/login`. |
| `/auth/login/` | `POST` | No | Authenticates credentials. Sets `refresh_token` cookie and returns `{ access, user, expires_in }`. |
| `/auth/refresh/` | `POST` | Cookie + CSRF | Exchanges `refresh_token` cookie for a new `{ access }` JWT. Requires `X-CSRFToken`. |
| `/auth/logout/` | `POST` | Bearer / Cookie | Clears cookie and blacklists refresh token. Requires `X-CSRFToken`. |
| `/auth/me/` | `GET` | Bearer | Returns the authenticated `UserProfile` object directly. |
| `/locations/` | `GET` | No | Returns flat list of 81 canonical micro-markets and allowed categorical values. |
| `/predictions/` | `POST` | Bearer | Submits property attributes, calls inference service, and stores record in DB. |
| `/predictions/` | `GET` | Bearer | Paginated history of authenticated user's predictions (`page`, `page_size`). |
| `/predictions/{id}/` | `GET` | Bearer | Single prediction detail record (strict ownership isolation; 404 for non-owners). |
| `/admin/summary/` | `GET` | Staff Bearer | Admin KPI summary (user counts, prediction volume, average prices). |
| `/admin/users/` | `GET` | Staff Bearer | Paginated admin user directory with search filter. |
| `/admin/predictions/`| `GET` | Staff Bearer | Paginated admin log of all platform predictions. |
| `/admin/reports/` | `GET` | Staff Bearer | Top micro-market volume and time-series aggregations. |
| `/admin/model/` | `GET` | Staff Bearer | Telemetry on active ML model version, parameters, and offline metrics. |

### 5.2 Error Response Envelope
Backend errors follow the contract schema defined in `contracts/application-api.yaml`:

```typescript
export interface ApiErrorEnvelope {
  error: {
    code: string;                          // e.g. "VALIDATION_ERROR", "UNAUTHORIZED"
    message: string;                       // Human-readable error message
    fields?: Record<string, string[]>;     // Specific form field errors
    request_id?: string;                   // Server correlation UUID for tracking
  };
}
```

---

## 6. Authentication & Session Lifecycle

1. **First Load / Browser Reload:**
   - Call `GET /api/v1/auth/csrf/` to store masked token in memory and receive `csrftoken` cookie.
   - Call `POST /api/v1/auth/refresh/` with `credentials: 'include'` and `X-CSRFToken`.
   - On success, store ephemeral `{ access }` in memory and fetch `GET /api/v1/auth/me/` to hydrate user profile.
   - On 401/403, set `user = null` and `authReady = true` gracefully without UI flicker.
2. **Single-Flight Refresh Promise:**
   - If multiple concurrent requests receive 401, only one refresh call is made; pending requests wait and retry once.
3. **Logout:**
   - Call `POST /api/v1/auth/logout/` and wipe in-memory token and user profile.

---

## 7. Page-by-Page Functional Requirements

### 7.1 Homepage (`/`) — Exactly Matching Design Reference
- **Hero Section:**
  - Left column: Eyebrow `"Real Estate Valuation Platform"`, H1 `"Know the Value. Find Your Place."`, subtext, `"Start Valuation →"` primary CTA, and `"Learn How It Works"` play button link.
  - Right column: High-resolution architectural villa terrace image (`/images/hero-clean.png`) with two floating data cards:
    - `"81 Micro-Markets"` with India map illustration.
    - `"₹26.94L MAE (Offline Test)"` with performance chart badge.
- **Why GharScope? Section:**
  - Left column: Headline `"Why GharScope?"` with value proposition and `"Our Approach →"` link.
  - Right column: 4 clean vertical pillars with round green badge icons:
    1. **Data Driven:** Real market data & ML-powered models.
    2. **Secure:** Your data & privacy come first.
    3. **Accurate:** Backed by proven ML performance.
    4. **Pan India:** 81 key micro-markets covered.
- **How It Works Section (Full-Width Forest Green Panel):**
  - Left: High-rise city balcony video thumbnail (`/images/how-it-works-thumb.png`) with play button.
  - Right: Eyebrow `"HOW IT WORKS"`, H2 `"Get Your Property Valuation in 3 Simple Steps"`, and 3 numbered step items:
    - `01 Enter Property Details` (Location, property type, size, layout).
    - `02 Review Estimate` (Data-driven value generated by ML model).
    - `03 Track History` (Save, benchmark, and revisit valuations).
- **Smarter Decisions Banner:**
  - Left: H2 `"Smarter Decisions. Greater Confidence."`, description, and `"Get Started →"` CTA.
  - Right: Modern architectural cantilever villa photograph (`/images/smart-decisions-villa.png`).

---

### 7.2 Property Catalogue (`/properties`) — Real Curated Showcase
- **Header & Architectural Banner:**
  - H1 `"Property Catalogue"`, subtext `"Discover a curated selection of premium properties across India's top cities."`, and modern architectural building banner (`/images/properties/catalogue-banner.png`).
- **Interactive Search Filter Bar:**
  - City dropdown, Property Type dropdown, Min Price dropdown, Max Price dropdown, and "Search" action button.
- **Sidebar Filters:**
  - Property Type checkboxes (Apartment, Independent House, Villa, Plot).
  - Bedrooms checkboxes (1 BHK, 2 BHK, 3 BHK, 4+ BHK).
  - Price Range checkboxes (₹0 - 50 L, ₹50 L - 1 Cr, ₹1 Cr - 2 Cr, ₹2 Cr+).
- **Benchmark Property Cards (6 Showcase Properties):**
  - Bangalore Whitefield (3 BHK Apartment, 1,450 sq.ft, ₹1.25 Cr, For Sale).
  - Pune Baner (4 BHK Villa, 2,800 sq.ft, ₹3.40 Cr, For Sale).
  - Mumbai Andheri West (2 BHK Apartment, 980 sq.ft, ₹1.85 Cr, For Sale).
  - Hyderabad Gachibowli (3 BHK Apartment, 1,650 sq.ft, ₹1.10 Cr, For Sale).
  - Delhi Gurgaon (4 BHK Villa, 3,200 sq.ft, ₹4.25 Cr, For Sale).
  - Chennai OMR (2 BHK Apartment, 1,050 sq.ft, ₹95 L, For Sale).
  - Each card includes high-res photo, specs, price in Lakhs/Crores, heart favorite toggle, and a **"Value this Property"** button that pre-populates `/predict`.

---

### 7.3 Property Price Prediction Calculator (`/predict`)
- **Authentication Gate:** Protected feature requiring sign-in. Guests selecting estimation are prompted with `/login?returnUrl=/predict`.
- **Dynamic Micro-Markets:** 81 canonical locations loaded dynamically from `GET /api/v1/locations/`.
- **11 Validated Inputs (Matching Contract):**
  - `location`: 81 indexed micro-markets (Required).
  - `area_value`: Numerical value between `100.0` and `20,000.0` sq.ft. (Required).
  - `area_basis`: Segmented control toggle between `CARPET` and `SUPER` (Required).
  - `bhk`: 1 to 10 integer selector (Optional).
  - `bathrooms`: 1.0 to 10.0 (Optional).
  - `balcony`: 0 to 10 (Optional).
  - `floor_number` & `total_floors`: Numeric inputs (Optional).
  - `parking_spaces`: 0 to 20 integer selector (Strictly `parking_spaces`, Treatment B logic).
  - `furnishing`: Furnished, Semi-Furnished, Unfurnished.
  - `transaction_type`: New Property, Resale, Rent/Lease, Other.
  - `status`: Ready to Move.
  - `facing` & `ownership`: Standard choices.
- **Valuation Result Card:**
  - Dual formatting: Lakhs / Crores (`₹1.25 Cr`) and exact (`₹1,25,00,000`).
  - Unit rate: `₹/sq.ft.`.
  - Recap of entered specs.
  - Error banners with retry buttons for 503 (service unready) and 504 (timeout).

---

### 7.4 User Authentication Pages (`/login` and `/register`)
- **Sign In (`/login`):** Email and password, visible error feedback, safe relative returnUrl redirection, link to register.
- **Sign Up (`/register`):** Display name, email, password ($\ge 8$ chars), field validation, redirects to `/login?registered=true`.

---

### 7.5 User Dashboard (`/dashboard`)
- List of user's past predictions fetched from `GET /api/v1/predictions/`.
- Responsive layout (desktop table and mobile cards).
- Detail modal for inspecting historical prediction parameters (`GET /api/v1/predictions/{id}/`).
- Quick CTA to re-run valuation with same parameters.

---

### 7.6 Staff Admin Portal (`/admin`)
- Accessible only to staff users (`is_staff: true`); clean 403 guard for regular users.
- Live telemetry from `GET /api/v1/admin/summary/`, `GET /api/v1/admin/reports/`, and `GET /api/v1/admin/model/`.
- Displays real platform stats: registered users, total valuations, active ML model version, and offline test metrics.

---

### 7.7 About & Methodology (`/about`)
- Transparent documentation of the LightGBM / HistGradientBoosting model pipeline.
- Explanation of **Carpet Area** vs. **Super Built-up Area**.
- Real offline test metrics ($R^2 = 0.7104$, $\text{MAE} = ₹26.94\text{L}$).
- Clear legal disclaimer that estimates are statistical market guides, not certified bank valuations.

---

## 8. Formatting & Localization Standards

### 8.1 Indian Rupee (INR) Formatter
Valuations must strictly use Indian numbering conventions (thousands, lakhs, crores):

```typescript
export function formatINRLakhCrore(amountInINR: number): string {
  if (amountInINR >= 10_000_000) {
    const crores = amountInINR / 10_000_000;
    return `₹${crores.toFixed(2)} Cr`;
  }
  if (amountInINR >= 100_000) {
    const lakhs = amountInINR / 100_000;
    return `₹${lakhs.toFixed(2)} L`;
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amountInINR);
}
```

### 8.2 Date & Timestamp Formatter
- Indian format: `23 Oct 2026, 04:15 PM IST` or short `23/10/2026`.

---

## 9. Implementation Execution Workstreams

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 5 EXECUTION WORKSTREAMS                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   Workstream 1: Foundation & Design System Tokens                                      │
│   - Setup globals.css with exact palette (#0F3D36, #1F5D52, #D4AF37, #F8F6F1).        │
│   - Configure Playfair Display & Inter web fonts.                                      │
│   - Build persistent Shell, Navbar, and Footer.                                        │
│                                                                                        │
│   Workstream 2: TypeScript Types & Typed API Client                                    │
│   - Define TypeScript interfaces matching contracts/application-api.yaml.              │
│   - Implement ApiClient with in-memory JWT, CSRF bootstrap, single-flight refresh.     │
│   - Write automated unit tests for API client and error envelope parsing.              │
│                                                                                        │
│   Workstream 3: Authentication Context & Session Management                            │
│   - Build AuthContext provider with reload hydration (/auth/refresh + /auth/me).       │
│   - Implement /login and /register with validation and safe returnUrl redirects.       │
│   - Write automated unit tests covering session restoration and refresh queue.         │
│                                                                                        │
│   Workstream 4: Brand Showcase & Property Catalogue Pages                              │
│   - Build Homepage (Hero with villa terrace visual, 4 pillars, How It Works panel).    │
│   - Build Property Catalogue (/properties) with interactive filters and 6 cards.      │
│   - Build About Page (Carpet vs Super, model metrics, transparency disclosure).        │
│                                                                                        │
│   Workstream 5: Property Price Prediction Calculator                                   │
│   - Implement /predict with 81 micro-market dropdown from GET /locations/.             │
│   - Build validated 11-field form with parking_spaces and Carpet/Super toggle.         │
│   - Build INR Lakh/Crore valuation results card with price per sq.ft.                  │
│                                                                                        │
│   Workstream 6: User Dashboard & Admin Telemetry Portal                                │
│   - Build /dashboard with real GET /predictions/ paginated history and detail modal.   │
│   - Build /admin with live summary KPIs, top locations, and active model telemetry.    │
│                                                                                        │
│   Workstream 7: Quality Gate & Full Verification                                       │
│   - Execute npm.cmd test (API client, session restore, formatters).                    │
│   - Execute npm.cmd run lint, npm.cmd run typecheck, and npm.cmd run build.           │
│   - Cross-service validation across Next.js (:3000), Django (:8000), FastAPI (:8001). │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Acceptance Criteria & Definition of Done

1. **Design System Fidelity:** 100% adherence to `DesignReference/GharScope Real Estate Design System.png`. Zero generic AI shapes or fake 3D cubes.
2. **Contract Compliance:** All requests match `contracts/application-api.yaml` exactly; zero invented routes or parameters.
3. **Security Integrity:** Access token stored in-memory only; refresh token managed via HttpOnly cookie; CSRF tokens passed on all mutating requests.
4. **Form Integrity:** Input field strictly named `parking_spaces` (range 0–20); micro-markets loaded dynamically from backend.
5. **Data Transparency:** Holdout metrics clearly labeled ($R^2 = 0.7104$, MAE ₹26.94L); zero fabricated metrics or testimonials.
6. **Automated Verification:**
   - `npm.cmd test`: All unit & integration tests pass cleanly.
   - `npm.cmd run lint`: 0 errors, 0 warnings.
   - `npm.cmd run typecheck`: 0 TypeScript errors.
   - `npm.cmd run build`: All static and dynamic pages compile successfully.
7. **Git Hygiene:** No commits created until explicit review and approval.
