# GharScope — Design Tokens

> **Product:** GharScope — Real Estate Price Prediction Platform (India)  
> **Tagline:** *Know the Value. Find Your Place.*  
> **Direction:** Ivory Luxury — light, editorial, trustworthy, architectural  
> **Status:** Frontend implementation reference  
> **Styling:** Vanilla CSS + CSS custom properties; no runtime styling library

---

## 1. Design Intent

GharScope should feel like a carefully art-directed Indian real-estate product, not a generic property template. The core interface uses warm ivory surfaces, deep forest green for primary actions and important panels, restrained gold accents, editorial serif headings, and high-quality architectural photography.

### Principles

- **Luxury without clutter:** use whitespace, typography, aligned grids, and photography—not gradients, excessive shadows, or decorative shapes.
- **Data before decoration:** property attributes, prices, forms, result states, and disclosures must remain easy to scan.
- **Light by default:** catalogue, forms, dashboard, login, and register use ivory/white surfaces. Reserve dark green for high-impact sections such as the How It Works band and valuation result panel.
- **Consistent components:** buttons, inputs, badges, borders, and spacing should behave the same across all pages.
- **Truthful UI:** never show invented live listings, testimonials, partner logos, model metrics, property predictions, or animated counters. Distinguish curated showcase/demo catalogue data from verified live listings.
- **Quiet motion:** use short native CSS transitions only. Respect reduced-motion preferences.

## 2. Color Tokens

The brand colors below are taken from the frontend requirements. Additional semantic tokens map those colors to interface roles.

```css
:root {
  /* Brand palette — source-defined */
  --color-primary: #0F3D36;          /* Deep Forest Green */
  --color-primary-dark: #0A261F;     /* Obsidian Forest */
  --color-secondary: #1F5D52;        /* Secondary Green */
  --color-gold: #D4AF37;             /* Accent Gold */

  /* Surfaces — source-defined */
  --color-ivory: #F8F6F1;             /* Main page canvas */
  --color-surface: #FFFFFF;           /* Cards and form surfaces */
  --color-surface-subtle: #F1F5F9;    /* Subtle field backgrounds */
  --color-border: #E2E8F0;            /* Standard borders */
  --color-border-subtle: #EDEAE2;     /* Warm dividers */

  /* Text — source-defined */
  --color-dark: #0F172A;              /* Primary text */
  --text-secondary: #64748B;          /* Body/supporting text */
  --text-muted: #94A3B8;              /* Quiet metadata */
  --text-on-dark: #FFFFFF;            /* Text on dark green */

  /* System states — source-defined */
  --color-error: #DC2626;
  --color-success: #16A34A;
  --color-warning: #D97706;

  /* Semantic aliases */
  --color-page: var(--color-ivory);
  --color-panel: var(--color-surface);
  --color-panel-subtle: var(--color-surface-subtle);
  --color-heading: var(--color-primary-dark);
  --color-body: var(--color-dark);
  --color-muted: var(--text-secondary);
  --color-focus: var(--color-secondary);
  --color-link: var(--color-primary);
  --color-link-hover: var(--color-secondary);
  --color-button-primary-bg: var(--color-primary);
  --color-button-primary-hover: var(--color-primary-dark);
  --color-button-primary-text: #FFFFFF;
  --color-button-secondary-bg: transparent;
  --color-button-secondary-border: var(--color-primary);
  --color-button-secondary-text: var(--color-primary);
}
```

### Color usage rules

| Color | Use it for | Avoid |
|---|---|---|
| `#0F3D36` Forest Green | Primary CTA, active navigation, selected states, important labels | Making every surface dark |
| `#0A261F` Obsidian Forest | How It Works panel, selected result panels, dark footer sections | Long form-heavy pages |
| `#1F5D52` Secondary Green | Hover states, secondary emphasis, selected controls | Competing with primary green |
| `#D4AF37` Gold | Small accents, active underline, icon detail, fine separator | Large blocks, body text, multiple gold buttons together |
| `#F8F6F1` Warm Ivory | Main page canvas and editorial sections | Low-contrast text directly on top of images |
| `#FFFFFF` White | Cards, forms, menus and elevated surfaces | Stacking too many nested white cards |
| `#E2E8F0` / `#EDEAE2` | Input borders, card edges and dividers | Heavy decorative outlines |

**Gold is an accent, not the main interaction color.** Primary actions stay forest green. Do not introduce neon colors or decorative gradients.

## 3. Typography Tokens

Use `Playfair Display` for display and section headings, and `Inter` for interface/body text. In Next.js, load the fonts through `next/font/google` and expose them as CSS variables rather than adding a blocking CSS `@import`.

```css
:root {
  --font-display: "Playfair Display", Georgia, "Times New Roman", serif;
  --font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --text-display: clamp(2.75rem, 5vw, 4.25rem);
  --text-h1: clamp(2.4rem, 4.6vw, 4rem);
  --text-h2: clamp(1.85rem, 3vw, 2.75rem);
  --text-h3: clamp(1.25rem, 2vw, 1.5rem);
  --text-h4: 1.125rem;
  --text-body: 1rem;
  --text-body-small: 0.875rem;
  --text-caption: 0.75rem;
  --text-label: 0.8125rem;

  --leading-display: 1.08;
  --leading-heading: 1.2;
  --leading-body: 1.6;
  --leading-compact: 1.35;

  --tracking-eyebrow: 0.08em;
}
```

### Type rules

- Hero/display headings: `Playfair Display`, weight 500–600, compact line-height.
- Section headings: `Playfair Display`, weight 500–600.
- Body copy, filters, form labels, prices, navigation, and buttons: `Inter`.
- Eyebrows: small uppercase Inter, medium/semibold, restrained letter spacing, gold or secondary text.
- Body copy should usually be 16px or larger; keep metadata readable and do not shrink important prices or form labels.
- Do not use serif typography for every field, badge, or control. Contrast serif headings with a clean sans-serif interface.

## 4. Spacing, Container and Grid Tokens

The following spacing/layout values are implementation conventions for consistent page composition.

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;  /* 4px */
  --space-2: 0.5rem;   /* 8px */
  --space-3: 0.75rem;  /* 12px */
  --space-4: 1rem;     /* 16px */
  --space-5: 1.25rem;  /* 20px */
  --space-6: 1.5rem;   /* 24px */
  --space-8: 2rem;     /* 32px */
  --space-10: 2.5rem;  /* 40px */
  --space-12: 3rem;    /* 48px */
  --space-16: 4rem;    /* 64px */
  --space-20: 5rem;    /* 80px */

  --container-max: 80rem;       /* 1280px */
  --container-reading: 46rem;    /* 736px */
  --page-gutter: clamp(1rem, 4vw, 3.5rem);
  --section-space-y: clamp(3.5rem, 7vw, 6rem);
  --grid-gap: 1.5rem;
  --grid-gap-tight: 1rem;
}
```

### Layout rules

- Center the main content in `--container-max`; use `--page-gutter` on both sides.
- Align section headings, grids, and content edges to the same container.
- Desktop catalogue: sidebar filters plus a flexible property-card grid. Use three cards per row when available width allows; reduce columns as the viewport narrows.
- Homepage hero: editorial split layout with text/search on one side and architectural photography on the other. Let the image create impact; do not layer many floating widgets over it.
- Prediction screen: use a clear form area paired with a distinct estimated-value/result panel. On mobile, stack the result after the form.
- Use consistent vertical rhythm; don't give every section a different layout pattern just for novelty.

## 5. Shape, Border and Elevation Tokens

```css
:root {
  --radius-xs: 0.25rem;
  --radius-sm: 0.375rem;
  --radius-md: 0.625rem;
  --radius-lg: 0.875rem;
  --radius-pill: 999px;

  --border-width: 1px;
  --border-default: var(--border-width) solid var(--color-border);
  --border-warm: var(--border-width) solid var(--color-border-subtle);

  --shadow-card: 0 4px 18px rgb(15 23 42 / 5%);
  --shadow-popover: 0 12px 32px rgb(15 23 42 / 10%);
}
```

### Surface rules

- Prefer a clean 1px border over a heavy shadow.
- Use a subtle card shadow only when it helps separate a surface from the page.
- Keep radii modest and consistent; avoid very round, pill-shaped cards everywhere.
- Avoid glassmorphism, glowing outlines, 3D cards, oversized gradients, and decorative blobs.
- Don't nest multiple bordered/shadowed containers without a functional reason.

## 6. Component Tokens and Behavior

### Navigation

- Header: warm ivory or white surface, thin warm divider, fixed-height spacing, logo on the left, primary navigation and account actions on the right.
- Active route: dark green text with a restrained gold underline or equivalent clear indicator.
- Keep navigation simple: Home, Properties, How It Works, About; include sign-in/account actions as appropriate.
- Mobile navigation must be keyboard accessible and must not obscure page content without a clear close action.

### Buttons

```css
:root {
  --button-height-sm: 2.25rem;
  --button-height-md: 2.75rem;
  --button-height-lg: 3.25rem;
  --button-padding-x: 1.25rem;
  --button-radius: var(--radius-sm);
  --button-font-size: 0.875rem;
  --button-font-weight: var(--font-weight-semibold);
  --control-transition: 160ms ease;
}
```

- **Primary:** forest green fill, white text; hover to obsidian forest.
- **Secondary:** transparent/ivory fill, green border and text.
- **Tertiary/link:** text-only, with clear hover/focus treatment.
- Use concise action labels: `Start Valuation`, `Search`, `Value this Property`, `Learn How It Works`.
- Show disabled, loading, success, and failure states where relevant. Never imply an operation succeeded before the API responds.

### Inputs and filters

- Inputs/selects: white surface, subtle 1px border, readable labels, consistent control height and spacing.
- Provide visible labels; placeholders are hints, not replacements for labels.
- Focus: clear, accessible ring using `--color-focus`; never remove the keyboard focus indicator.
- Validation/error copy appears beside the related field and is not conveyed by color alone.
- Catalogue filters: city, property type, min/max price, bedrooms and price bands. Make the applied filter state and reset action clear.
- Use checkbox/radio/segmented controls only for choices that match the input semantics.

### Property cards

- Use a consistent image ratio around 3:2 across catalogue cards.
- Put status/category in a small, high-contrast badge on the image only when the status is known.
- Recommended content order: image → location → property type/BHK → area → price → action.
- Keep prices visually prominent, formatted using Indian lakh/crore conventions from the frontend requirements.
- Favourite control needs an accessible name and an obvious active state.
- `Value this Property` should pass the selected property's real available attributes into `/predict`; don't silently invent missing values.
- The six properties named in the requirements are showcase/demo entries, not verified live listings. Label them honestly if they appear in the UI.

### Valuation result panel

- A deep-green panel is a deliberate contrast element on the otherwise light prediction page.
- Show an estimate only after a successful backend prediction response.
- Present the main amount in lakh/crore format and, where available, the exact Indian-numbering amount and price per square foot.
- Include a recap of the submitted property attributes and a clear statistical-estimate disclaimer.
- Do not draw historical trends or future appreciation charts unless the backend actually supplies the required data. Don't show a made-up sample amount as a real prediction.
- For `503` and `504`, use clear unavailable/timeout states and a retry action; preserve form inputs where practical.

### Status and feedback

- Success, warning, and error colors use the semantic tokens in section 2.
- Pair status color with an icon/label and text so meaning is not color-only.
- Loading states should be restrained and should not create fake counters or simulated live metrics.
- Empty states explain what is missing and provide one relevant next action.

## 7. Page-Level Visual Direction

### Homepage (`/`)

1. Header and hero: eyebrow `Real Estate Valuation Platform`; heading `Know the Value. Find Your Place.`; concise copy; primary `Start Valuation` CTA and secondary `Learn How It Works` action.
2. Hero image: a high-quality architectural villa terrace image with natural daylight/golden-hour light. If floating metric cards are used, limit them to the two approved metrics: `81 Micro-Markets` and `₹26.94L MAE (Offline Test)`.
3. Four trust pillars: Data Driven, Secure, Accurate, Pan India. Use simple outline icons and short factual descriptions.
4. How It Works: full-width obsidian-forest panel with three numbered steps and an architectural video thumbnail if a real asset exists.
5. Smarter Decisions banner: short copy, one CTA, one strong architectural image.

### Property Catalogue (`/properties`)

- A short architectural banner, title, explanatory text, and clear search/filter bar.
- Sidebar filters for property type, bedroom count, and price band; adapt to a drawer or collapsible panel on smaller screens.
- Six requirement-defined showcase cards: Bangalore Whitefield, Pune Baner, Mumbai Andheri West, Hyderabad Gachibowli, Delhi Gurgaon, Chennai OMR.
- Keep the layout image-led but information-dense enough for users to compare price, BHK, and area quickly.
- If data is static showcase content, label it as demo/showcase data. Do not add invented review scores, agent profiles, availability claims, or partner marks.

### Prediction (`/predict`)

- Light, focused form UI, with an explicit title, explanation, labels, required-field markers, and inline validation.
- Preserve the contract field name `parking_spaces` and the Carpet/Super area-basis selector.
- Load the 81 canonical micro-markets from `GET /api/v1/locations/`; do not hardcode a fabricated list as live data.
- Keep the estimate panel in an empty/pre-submit state until a real prediction response arrives.
- Keep the disclaimer visible: the result is a statistical market guide, not a certified bank valuation.

### Login and Register

- Simple centered form surface, minimal distractions, clear field errors, password requirements, and links between sign-in and registration.
- Use the same spacing, inputs, button, and focus tokens as the main application.

### Dashboard and Admin

- Dashboard: use a readable table on desktop and stacked cards on mobile; prioritize valuation amount, date, location and a re-run action.
- Admin: present only values returned by staff-authorized endpoints. Distinguish real platform statistics from offline model evaluation metrics.
- Do not create charts or KPIs from placeholder data without an explicit demo label.

### About (`/about`)

- Explain model methodology, Carpet Area vs Super Built-up Area, and the limitations of a statistical estimate.
- The requirements specify real offline holdout metrics: `R² = 0.7104`, `MAE = ₹26.94L`, `RMSE = ₹85.18L`. Label these as offline holdout evaluation metrics, not live user prediction accuracy.

## 8. Photography and Iconography

### Photography

- Use real, high-resolution architectural photography with coherent lighting and a consistent crop treatment.
- Preferred subjects: contemporary Indian homes, terraces, apartment buildings, villas, and credible urban residential settings.
- Prefer licensed/owned images from a consistent source. Optimize images and provide meaningful alt text.
- Avoid imagery with visible watermarks, fake brand signage, surreal architecture, inconsistent perspective, or obvious compositing artifacts.
- Avoid reusing the same hero image in every section. Use a small, curated set of related images.
- Do not place important text directly over a busy photograph unless a solid/adequate contrast surface protects readability.

### Icons

- Use Lucide React outline icons with consistent stroke weight and size.
- Use icons to clarify meaning; pair ambiguous icons with labels.
- Do not mix outline, 3D, emoji, filled, and hand-drawn icon styles in one interface.
- No decorative 3D cubes, WebGL objects, or animated icon effects.

## 9. Responsive Tokens and Rules

```css
:root {
  --breakpoint-sm: 40rem;   /* 640px */
  --breakpoint-md: 48rem;   /* 768px */
  --breakpoint-lg: 64rem;   /* 1024px */
  --breakpoint-xl: 80rem;   /* 1280px */
}
```

CSS custom properties can't themselves be used as media-query conditions in all standard CSS workflows, so write media queries using the literal values above or centralize breakpoints in the project's chosen build tooling.

- **Small screens:** stack hero columns and valuation panels; make catalogue filters collapsible; use full-width primary CTAs when space is tight.
- **Medium screens:** reduce property grid to two columns where suitable and allow header items to compact.
- **Large screens:** use the editorial split hero, three-column catalogue grid, and side-by-side prediction form/result.
- Prevent horizontal overflow, ensure long prices/city names wrap safely, and keep touch targets comfortably large.
- Images should keep their intended crop without stretching.

## 10. Motion, Accessibility and Performance

```css
:root {
  --duration-fast: 120ms;
  --duration-normal: 160ms;
  --duration-slow: 220ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

- Prefer native scrolling and simple CSS transitions. No Lenis, heavy GSAP, Three.js, or WebGL for routine interface effects.
- Every interactive control must work with keyboard input and have a visible focus state.
- Keep text contrast readable on ivory, white, and dark-green surfaces.
- Use semantic HTML, real form labels, descriptive link text, and meaningful image alt text.
- Optimize large image assets; avoid loading below-the-fold imagery eagerly without need.

## 11. Data, Privacy and Trust Rules

- The browser calls Django REST endpoints only; it must never call the FastAPI inference service directly.
- Access JWT stays in memory; refresh token is handled by the HttpOnly cookie flow described in the frontend requirements. Never store credentials or tokens in `localStorage` or URL query parameters.
- Follow the API contract for CSRF, authorization, errors, bounded retries, and session refresh.
- Use actual backend responses for user predictions, history, admin statistics and location lists.
- Display offline metrics only with the exact offline-evaluation context; don't present them as a guarantee for an individual property.
- Use Indian Rupee conventions consistently: `₹1.25 Cr`, `₹26.94L`, and `₹1,25,00,000` where appropriate.

## 12. Suggested Global CSS Starter

This is a starting point for `app/globals.css`; keep component-specific styles near the component when that improves maintainability.

```css
* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background: var(--color-page);
  color: var(--color-body);
  font-family: var(--font-body);
  font-size: var(--text-body);
  line-height: var(--leading-body);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

h1,
h2,
h3,
h4 {
  margin: 0;
  color: var(--color-heading);
  font-family: var(--font-display);
  font-weight: var(--font-weight-medium);
  line-height: var(--leading-heading);
}

p {
  margin: 0;
}

a {
  color: var(--color-link);
  text-underline-offset: 0.18em;
}

a:hover {
  color: var(--color-link-hover);
}

button,
input,
select,
textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

:focus-visible {
  outline: 3px solid var(--color-focus);
  outline-offset: 3px;
}

.container {
  width: min(100% - (2 * var(--page-gutter)), var(--container-max));
  margin-inline: auto;
}

.section {
  padding-block: var(--section-space-y);
}
```

## 13. Final Acceptance Checklist

- [ ] The interface follows Ivory Luxury: warm ivory canvas, forest-green actions, restrained gold, Playfair Display headings, Inter UI.
- [ ] Catalogue filters, property cards, forms, buttons, and status messages use consistent tokens.
- [ ] The home hero and property cards use coherent, high-quality architectural images.
- [ ] All six requirement-defined properties are explicitly treated as showcase/demo entries unless verified listing data is provided.
- [ ] No fabricated predictions, charts, listings, testimonials, partner logos, or animated counters appear as real data.
- [ ] Offline evaluation values are labeled correctly: `R² = 0.7104`, `MAE = ₹26.94L`, `RMSE = ₹85.18L`.
- [ ] All responsive layouts work without horizontal overflow.
- [ ] Interactive controls have accessible labels, keyboard operation, visible focus, and meaningful error/loading/empty states.
- [ ] Frontend uses CSS variables and lightweight native CSS transitions; no unnecessary animation/WebGL libraries are introduced.
- [ ] API calls follow the backend contracts and never call the inference microservice directly from the browser.

---

**Implementation note:** The palette and core type hierarchy above follow the requirements specification. Spacing, radii, shadows, breakpoints and interaction timings are implementation-level design decisions introduced here to make the system consistent; tune them only when an approved design reference requires a deliberate change.
