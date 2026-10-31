---
name: apple-design-ui-ux
description: Apple Design, Fluid Typography, Micro-interactions, and UI-UX Pro Max Guidelines. Enforces luxury aesthetics, liquid glassmorphism, responsive tactile feedback, and WCAG 2.2 AA accessibility.
---

# Apple Design & UI-UX Pro Max Guidelines

## 1. Aesthetic Philosophy
Luxury digital experiences should feel effortless, understated, and tactile:
- **Depth & Dimension:** Subtle layering using blur effects (`backdrop-filter: blur(20px)`), frosted glass surfaces (`rgba(255, 255, 255, 0.05)`), and soft multi-stop box shadows.
- **Palette Hierarchy:** Rich dark foundations (`#0A0A0C`, `#121216`) paired with warm metallic accents (`#D4AF37`, `#E5C158`) and neutral off-white typography (`#F5F5F7`, `#A1A1A6`).
- **Typography:** Clean geometric sans-serif hierarchy (SF Pro / Inter / Instrument Sans) with generous line heights (1.5–1.7) and balanced letter spacing.

## 2. Micro-Interactions & Motion
- **Natural Physics:** Easing curves tuned to authentic deceleration (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Tactile Feedback:** Subtle scale adjustments on hover (`transform: scale(1.02)` or `translateY(-2px)`) with transitions of 200ms–300ms.
- **Reduced Motion Support:** Always wrap transitions in `@media (prefers-reduced-motion: reduce)` to disable heavy animations for users with vestibular sensitivities.
- **Mobile Touch Handling:** Configure smooth iOS scrolling with `-webkit-overflow-scrolling: touch` and `touch-action: manipulation` on buttons to prevent 300ms click delay.

## 3. Accessibility & Usability (WCAG 2.2 AA)
- **Contrast Ratios:** Text must maintain at least 4.5:1 contrast against adjacent backgrounds (7:1 for enhanced contrast).
- **Interactive Targets:** Buttons and clickable links must have a minimum touch target size of 44x44 CSS pixels.
- **Semantic Structure:** Use appropriate landmark tags (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`) and provide descriptive `aria-label` attributes on icon-only interactive controls.
- **Focus Rings:** Ensure visible focus indicators for keyboard-only navigation using high-contrast outline styling.
