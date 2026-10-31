---
name: browserbase-ui-test
description: Automated UI testing, visual regression verification, and headless browser validation protocols.
---

# Browserbase & Headless UI Testing Protocols

## 1. Scope & Objective
Automated UI testing validates that user interfaces render without visual regression, layout breaks, console errors, or broken media across responsive viewports.

## 2. Core Testing Principles
- **Hermetic Executions:** Tests must run deterministically with zero dependence on external network states.
- **Console Hygiene:** Tests must assert that zero uncaught JavaScript exceptions or 404 resource errors occur during page lifecycle.
- **Viewport Coverage:** Test critical flows across standard breakpoints:
  - Mobile: 375x667 (iPhone SE), 390x844 (iPhone 14)
  - Tablet: 768x1024 (iPad)
  - Desktop: 1280x800, 1920x1080
- **Visual Assertions:** Validate that critical visual elements (Hero section, audio players, video embeds, CTA buttons) maintain computed display and visibility attributes.
- **Assertion Rigor:** Never write vacuous assertions (`assert True`). Test failure modes explicitly (break-the-implementation verification).
