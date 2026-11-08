# PredictIQ Design System & Token Specification

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Design System Philosophy

The PredictIQ design system bridges data-dense scientific metrics with modern, accessible user interfaces. It is built around three core visual requirements:

1. **High Information Density with Visual Hierarchy:** Presenting complex statistical distributions, quantile intervals, and financial tables clearly without visual clutter.
2. **Defensible Contrast & Accessibility:** Strict adherence to WCAG 2.1 AA and AAA contrast ratios across both light mode and obsidian dark mode.
3. **Fluid Responsiveness:** Layouts adapt dynamically across desktop, tablet, and mobile displays using responsive CSS `clamp()` expressions rather than rigid breakpoints.

---

## 2. Color Palette & Token Hierarchy

Design tokens are declared as CSS custom properties in `frontend/src/index.css` and mapped to Tailwind CSS utility classes.

### 2.1. Brand & Semantic Status Tokens
```css
:root {
  /* Brand Core Palette */
  --color-primary: #1A56DB;        /* Deep Sapphire */
  --color-primary-dark: #1E40AF;
  --color-primary-light: #3B82F6;
  --color-primary-50: #EFF6FF;
  --color-primary-100: #DBEAFE;
  --color-primary-500: #3B82F6;
  --color-primary-600: #2563EB;
  --color-primary-700: #1D4ED8;

  /* Semantic Status Tokens */
  --color-success: #10B981;        /* Emerald */
  --color-warning: #F59E0B;        /* Amber */
  --color-danger: #EF4444;         /* Rose / Red */
  --color-info: #3B82F6;           /* Sky Blue */
}
```

### 2.2. Light Theme Surface & Text Palette (WCAG AAA)
```css
:root {
  --bg-primary: #F8FAFC;           /* Slate 50 canvas */
  --bg-surface: #FFFFFF;           /* Pure white card surface */
  --bg-elevated: #F1F5F9;          /* Slate 100 elevated elements */
  --bg-inset: #E2E8F0;             /* Slate 200 input backgrounds */
  
  --text-primary: #0F172A;         /* Slate 900 (Contrast: 16:1 against #FFF) */
  --text-secondary: #475569;       /* Slate 600 (Contrast: 5.8:1) */
  --text-tertiary: #64748B;        /* Slate 500 */
  --text-inverse: #FFFFFF;
  
  --border-color: #E2E8F0;         /* Slate 200 */
  --border-subtle: rgba(15, 23, 42, 0.06);
  --border-focus: #1A56DB;
}
```

### 2.3. Dark Theme Surface & Text Palette (Obsidian / Dark Mode)
Activated via `[data-theme="dark"]` or `:root.dark`:
```css
[data-theme="dark"], :root.dark {
  --bg-primary: #090D16;           /* Deep Obsidian */
  --bg-surface: #111827;           /* Midnight Gray */
  --bg-elevated: #1E293B;          /* Slate 800 */
  --bg-inset: #0B1120;             /* Recessed input wells */
  
  --text-primary: #F8FAFC;         /* Slate 50 (Contrast: 17.5:1 against #090D16) */
  --text-secondary: #CBD5E1;       /* Slate 300 (Contrast: 10.2:1 against #111827) */
  --text-tertiary: #94A3B8;        /* Slate 400 */
  --text-inverse: #0F172A;
  
  --border-color: #1E293B;         /* Slate 800 */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-focus: #3B82F6;
}
```

### 2.4. Statistical Quantile & Tier Tokens
```css
:root {
  /* Confidence Interval & Quantile Markers */
  --quantile-p10: #10B981;         /* Optimistic boundary (Emerald) */
  --quantile-p50: #2563EB;         /* Median estimate (Blue) */
  --quantile-p90: #F59E0B;         /* Conservative boundary (Amber) */
  --quantile-track: #E2E8F0;
  --quantile-band: linear-gradient(90deg, rgba(16, 185, 129, 0.25) 0%, rgba(37, 99, 235, 0.35) 50%, rgba(245, 158, 11, 0.25) 100%);
  --quantile-marker: #1E293B;

  /* Data Quality Tier Badges */
  --tier-a-bg: #ECFDF5; --tier-a-text: #065F46; --tier-a-border: #A7F3D0;
  --tier-b-bg: #EFF6FF; --tier-b-text: #1E40AF; --tier-b-border: #BFDBFE;
  --tier-c-bg: #FFFBEB; --tier-c-text: #92400E; --tier-c-border: #FDE68A;
}
```

---

## 3. Typography Scale & Font Architecture

- **Sans-Serif Font:** `Inter`, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif.
- **Monospace Font:** `JetBrains Mono`, `Fira Code`, `SF Mono`, Consolas, monospace.
- **Tabular Numerics:** All currency figures, hours, and statistical quantiles apply `.tabular-nums` (`font-variant-numeric: tabular-nums`) to ensure vertical column alignment across changing figures.

| Token | Rem Value | Pixel Value | Line Height | Application |
|---|---|---|---|---|
| `--text-2xs` | `0.6875rem` | 11px | `1.0rem` | Fine print, badge captions, axis sub-labels |
| `--text-xs` | `0.75rem` | 12px | `1.0rem` | Table headers, secondary tooltips, metadata |
| `--text-sm` | `0.875rem` | 14px | `1.25rem` | Form labels, standard table cells, navigation links |
| `--text-base` | `1.0rem` | 16px | `1.5rem` | Standard body prose, default inputs |
| `--text-lg` | `1.125rem` | 18px | `1.75rem` | Section headers, card titles |
| `--text-xl` | `1.25rem` | 20px | `1.75rem` | Modal headers, subheadings |
| `--text-2xl` | `1.5rem` | 24px | `2.0rem` | Page titles, key metric numbers |
| `--text-3xl` | `1.875rem` | 30px | `2.25rem` | Dashboard hero banners |
| `--text-4xl` | `2.25rem` | 36px | `2.5rem` | Marketing headlines |

---

## 4. Responsive Clamps & Fluid Layouts

Rather than jarring multi-breakpoint jumps, PredictIQ utilizes CSS `clamp(min, preferred, max)` to ensure proportional scaling across viewport widths:

```css
/* Navigation Bar Horizontal Inset */
padding: 0 clamp(1rem, 3vw, 1.5rem);

/* Main Dashboard & Content Container Gutters */
padding: clamp(1rem, 3vw, 2rem);

/* Hero & Major Page Headers */
font-size: clamp(1.75rem, 3vw, 2.5rem);

/* Landing Page Hero Heading */
font-size: clamp(2.25rem, 5vw, 3.75rem);

/* Manual Budget Page Container */
padding: clamp(16px, 3vw, 40px);
```

### Mobile Layout Adaptations ($<768\text{px}$)
- **Workspace Navigation:** Shifts from a vertical desktop sidebar (`232px` width) to a fixed bottom navigation rail (`min-height: 44px` touch targets) with safe-area insets (`env(safe-area-inset-bottom)`).
- **Multi-Step Wizard:** Step progress indicator switches from horizontal bar to compact stacked counter.
- **Card Grids:** Multi-column metric cards stack into single-column vertical cards to prevent horizontal overflow.
