# Open Decisions and Risk Register

## Real Estate Price Prediction Platform — India

The following decisions are open and must be formally resolved by the product owner before the dependent phase begins. None of these items are assumed to be completed or pre-approved.

---

## Decisions Log

| # | Topic | Description & Options | Last Permissible Phase | Status |
|---|---|---|---|---|
| **1** | **Inference Framework** | **FastAPI** is recommended for `inference-service/` due to Pydantic schema validation and low overhead. Alternative: Flask or minimal WSGI. | Phase 0 / Phase 3 Entry | **PROVISIONAL / REQUIRES OWNER APPROVAL** |
| **2** | **Dataset Licence & Provenance** | Verify the original source, redistribution rights, and commercial/academic licence terms for `house_prices.csv` before committing or publishing raw data. | Phase 1 Entry | **OPEN** |
| **3** | **Duplicate Record Policy** | 119,339 rows are duplicate occurrences across the 20 columns after excluding `Index`. Determine whether repeated rows represent repeated scraped listings (deduplicate) or genuine market transactions, and define group-aware train/test splitting to prevent data leakage. | Phase 1 | **OPEN** |
| **4** | **Target & Price Parsing** | Confirm parsing rules for `Amount(in rupees)` (e.g. `Lac`, `Cr`) and explicit exclusion of `Call for Price` (9,684 records) and unparseable values from supervised target training. | Phase 1 | **OPEN** |
| **5** | **Area Basis & Unit Policy** | Carpet Area and Super Area must not be conflated. Define explicit conversion factors for verified units (sqft, sqm, sqyrd) and reject unknown regional units. | Phase 1 | **OPEN** |
| **6** | **Supported Location Policy** | 81 raw location strings must be normalized (casing, aliases). Determine policy for unsupported or low-sample locations (strict error vs documented fallback). | Phase 1 | **OPEN** |
| **7** | **Authentication Mechanism** | Choose between HttpOnly Session cookies (traditional Django CSRF) vs Bearer JWT tokens for Next.js ↔ Django communication across local and production domains. | Phase 4 Entry | **OPEN** |
| **8** | **Dependency Pinning & Versions** | Select and freeze specific version ranges for Node.js (v24), Python (3.13), Django (5.1+), and scikit-learn (1.6+) across local development and future containers. | Phase 0 / Phase 1 | **IN REVIEW** |
| **9** | **Production Hosting & Database** | Confirm cloud hosting providers (e.g., Vercel for Next.js, Render/Fly.io/AWS for Django and FastAPI, managed PostgreSQL). | Phase 8 Entry | **DEFERRED TO PHASE 8** |
| **10** | **Data Retention & Export Privacy** | Define user account deletion policy, prediction history retention TTL, and allowed column allowlist for admin CSV reports. | Phase 4 / Phase 8 | **OPEN** |
