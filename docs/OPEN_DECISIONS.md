# Decisions and Risk Register

## Real Estate Price Prediction Platform — India

| Document field | Details |
|---|---|
| Status | Synchronized with Product Owner Approvals (Phase 0 Alignment) |
| Last updated | 22 October 2026 |

---

## 1. Decisions Log

| # | Topic | Description & Resolution | Phase | Status |
|---|---|---|---|---|
| **1** | **Inference Framework** | **FastAPI** is approved for `inference-service/` for standalone HTTP serving, native Pydantic schema validation, and asynchronous execution. | Phase 0 | **APPROVED** |
| **2** | **Dataset Licence & Provenance** | Verify the original source, redistribution rights, and commercial/academic licence terms for `house_prices.csv` before committing or publishing raw data. | Phase 1 Entry | **OPEN (Blocks Phase 1)** |
| **3** | **Duplicate Record Policy** | 119,339 rows are duplicate occurrences across 20 columns after dropping `Index`. Audit exact and near-duplicates before data split; do not blindly delete without evidence. Establish leakage-aware split after investigation. | Phase 1 | **OPEN (Pending Phase 1 Evidence)** |
| **4** | **Target & Price Parsing** | Approved principles: parse Lac/Cr into numeric INR deterministically; exclude `Call for Price` (9,684 records) and unparseable values from supervised target training. Final counts pending audit. | Phase 1 | **PRINCIPLES APPROVED (Counts Pending Phase 1)** |
| **5** | **Area Basis & Unit Policy** | Approved principles: Carpet Area and Super Area must not be conflated. Convert only verified units (sqft, sqm, sqyrd); do not guess unknown regional units. Conversion tables pending audit. | Phase 1 | **PRINCIPLES APPROVED (Outcomes Pending Phase 1)** |
| **6** | **Supported Location Policy** | 81 raw location strings must be normalized (casing, aliases). Supported location policy and low-sample handling to be finalized from audit. | Phase 1 | **OPEN (Pending Phase 1 Evidence)** |
| **7** | **Authentication Mechanism** | **Django REST Framework with SimpleJWT** is approved. Browser pattern: short-lived access JWT held in memory by frontend; refresh token stored in HttpOnly cookie (Secure in production HTTPS, environment SameSite/domain/path, rotation/revocation, logout invalidation, CSRF protection for cookie-backed refresh/logout). No long-lived tokens in localStorage. Authoritative backend permissions. Design approved; implementation scheduled for Phase 4. | Phase 0 (Design) / Phase 4 (Impl) | **DESIGN APPROVED (Implementation Phase 4)** |
| **8** | **Dependency Pinning & Versions** | Pinned to supported lines: Next.js 16.4.2 (Active LTS), React 19.0.0, Django 5.2.18 LTS, DRF 3.18.3, SimpleJWT 5.5.1, FastAPI 0.115.14, Python 3.13. | Phase 0 | **RESOLVED & PINNED** |
| **9** | **Database Strategy & Hosting** | Approved strategy: SQLite for local development; PostgreSQL for production deployment. Production settings strictly require PostgreSQL and fail clearly without silent SQLite fallback. Cloud hosting provider selection deferred to Phase 8. | Phase 0 (DB Strategy) / Phase 8 (Hosting) | **DB STRATEGY APPROVED (Host Deferred)** |
| **10** | **Data Retention & Export Privacy** | Define user account deletion policy, prediction history retention TTL, and allowed column allowlist for admin CSV reports. | Phase 4 / Phase 8 | **OPEN (Scheduled for Phase 4/8)** |
