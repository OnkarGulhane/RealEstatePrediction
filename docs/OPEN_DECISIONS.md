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
| **2** | **Dataset Licence & Provenance** | Technical audit complete. Public source investigated (Kaggle: Juhi Bhojani, CDLA-Sharing-1.0; scraped from Indian property portals). Designated **UNVERIFIED / RESTRICTED FROM REDISTRIBUTION**. Policy approved: all raw, interim, and processed CSV data remains local-only and excluded from Git via `.gitignore`. No public redistribution without evidenced rights-holder permission. | Phase 1 | **RESOLVED & POLICY APPROVED (2026-10-22)** |
| **3** | **Duplicate Record Policy** | Phase 1 audit measured 119,339 duplicate listing rows across 20 property columns (excluding `Index`), forming 68,192 unique property configurations. Approved Phase 2 policy: Primary training view in Phase 2 excludes exact duplicate property rows (excluding `Index`). Auditable row/group mapping preserved; raw CSV and full prepared output preserved. Evaluate grouping key for validation; if no reliable grouping key exists, document limitation and avoid claiming `GroupKFold`. No deduplicated training view created yet. | Phase 1 / Phase 2 | **POLICY APPROVED FOR PHASE 2 (2026-10-22)** |
| **4** | **Target & Price Parsing** | Deterministic parser verified on all 187,531 rows. Valid supervised target: 177,847 rows (112,568 Lac/Lakh + 65,279 Cr/Crore). Excluded `Call for Price`: 9,684 rows. Unparseable / Blank: 0 rows. 100% exact reconciliation. | Phase 1 | **RESOLVED & VERIFIED (2026-10-22)** |
| **5** | **Area Basis & Unit Policy** | Strict separation verified: Carpet Area only (106,858), Super Area only (79,846), Both (0), Neither (827); Sum = 187,531 (100% exact). 30 regional-unit listings preserved (10 Carpet, 20 Super) with missing standardized sqft. Approved Phase 2 policy: maintain separate features with presence indicators; no carpet-to-super ratio. | Phase 1 / Phase 2 | **POLICY APPROVED FOR PHASE 2 (2026-10-22)** |
| **6** | **Supported Location Policy** | Audit identified 81 raw location strings with micro-market and city combinations. Standardized parsing and threshold policy scheduled for Phase 2 feature engineering. | Phase 1 / Phase 2 | **OPEN (Scheduled for Phase 2)** |
| **7** | **Authentication Mechanism** | **Django REST Framework with SimpleJWT** is approved. Browser pattern: short-lived access JWT held in memory by frontend; refresh token stored in HttpOnly cookie (Secure in production HTTPS, environment SameSite/domain/path, rotation/revocation, logout invalidation, CSRF protection for cookie-backed refresh/logout). No long-lived tokens in localStorage. Authoritative backend permissions. Design approved; implementation scheduled for Phase 4. | Phase 0 (Design) / Phase 4 (Impl) | **DESIGN APPROVED (Implementation Phase 4)** |
| **8** | **Dependency Pinning & Versions** | Pinned to supported lines: Next.js 16.4.2 (Active LTS), React 19.0.0, Django 5.2.18 LTS, DRF 3.18.3, SimpleJWT 5.5.1, FastAPI 0.115.14, Python 3.13. | Phase 0 | **RESOLVED & PINNED** |
| **9** | **Database Strategy & Hosting** | Approved strategy: SQLite for local development; PostgreSQL for production deployment. Production settings strictly require PostgreSQL and fail clearly without silent SQLite fallback. Cloud hosting provider selection deferred to Phase 8. | Phase 0 (DB Strategy) / Phase 8 (Hosting) | **DB STRATEGY APPROVED (Host Deferred)** |
| **10** | **Data Retention & Export Privacy** | Define user account deletion policy, prediction history retention TTL, and allowed column allowlist for admin CSV reports. | Phase 4 / Phase 8 | **OPEN (Scheduled for Phase 4/8)** |
