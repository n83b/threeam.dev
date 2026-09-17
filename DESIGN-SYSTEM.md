# Three AM Prototype Design System

The approved homepage remains the visual source of truth. The shared stylesheet (`styles.css`) is the implementation source for these tokens and component conventions.

## Tokens

- **Ink:** `--ink` `#15231e`; primary text and dark surfaces
- **Paper / white:** `--paper` `#f4f2eb`, `--white` `#fffefa`
- **Original Three AM blue:** `--blue` `#3498db`; shared interactive and interface accent
- **Supporting accents:** `--lime`, `--coral`, `--violet`
- **Type:** `--font-display` (Manrope) for all body/display copy; `--font-mono` (DM Mono) for eyebrow labels, dates and microcopy
- **Spacing:** `--space-1` through `--space-7` (`.5rem` to `8.5rem`)
- **Radii:** `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-round`
- **Motion:** `--ease`, used for restrained 200–600ms hover transitions. Motion is reduced under `prefers-reduced-motion`.

## Reusable components

- Shared header, logo treatment, desktop/mobile navigation and mobile-menu control
- Shared footer and contact CTA
- Buttons: `.button-primary`, `.button-outline`; inline `.text-link`
- Cards: service cards, project cards and related-service cards
- Page patterns: `.page-hero`, `.breadcrumbs`, `.content-grid`, `.side-nav`, `.service-list`, `.image-band-grid`
- Responsive breakpoints: tablet at 900px and phone at 560px
- Accessibility: skip link, semantic navigation labels, descriptive image alternatives, visible `:focus-visible` outline, mobile navigation state via `aria-expanded`, and reduced-motion styles.

## Interior-page URL decision

- **New:** `/services/` provides a consolidated services overview that did not exist in the audited sitemap.
- **Preserved:** `/web/` remains the existing Web Solutions URL and now acts as the detailed Web Design & Development representative page.
