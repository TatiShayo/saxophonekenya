/**
 * nav.js — Navigation bar, mobile drawer and scroll-spy
 * --------------------------------------------------------------------------
 * Fixes carried over from the original inline script:
 *  - Hamburger had no aria-expanded / aria-controls, so screen-reader users
 *    could not tell whether the menu was open.
 *  - Drawer had no Escape handler and no outside-click handler.
 *  - No focus trap while the drawer is open, so tabbing walked into the
 *    page behind the overlay.
 *  - No scroll-spy, so the active section was never highlighted.
 *  - closeDrawer() was a bare global relied upon by inline onclick handlers.
 */

import { qs, qsa, openExternal } from './utils.js';
import { CONFIG } from './config.js';

const FOCUSABLE = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';

const nav = {
  hamburger: null,
  drawer: null,
  lastFocus: null
};

function isOpen() {
  return nav.hamburger?.getAttribute('aria-expanded') === 'true';
}

function setDrawer(open) {
  if (!nav.hamburger || !nav.drawer) return;
  nav.hamburger.setAttribute('aria-expanded', String(open));
  nav.drawer.classList.toggle('active', open);
  nav.drawer.setAttribute('aria-hidden', String(!open));
  document.body.style.overflow = open ? 'hidden' : '';

  if (open) {
    nav.lastFocus = document.activeElement;
    /* Move focus into the drawer so keyboard users land in the menu. */
    const first = nav.drawer.querySelector(FOCUSABLE);
    if (first) first.focus();
  } else if (nav.lastFocus instanceof HTMLElement) {
    nav.lastFocus.focus();
    nav.lastFocus = null;
  }
}

/** Kept as a global: rate-card.html and several templates reference it. */
export function closeDrawer() { setDrawer(false); }
window.closeDrawer = closeDrawer;

function trapFocus(event) {
  if (!isOpen() || event.key !== 'Tab') return;
  const items = qsa(FOCUSABLE, nav.drawer).filter(n => n.offsetParent !== null);
  if (!items.length) return;

  const first = items[0];
  const last = items[items.length - 1];

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

   Scroll-spy — highlight the nav link for the section in view
   -------------------------------------------------------------------------- */
function initScrollSpy() {
  const links = qsa('.nav-menu a[href^="#"]');
  if (!links.length || !('IntersectionObserver' in window)) return;

  const byId = new Map();
  for (const link of links) {
    const target = document.getElementById(link.hash.slice(1));
    if (target) byId.set(target, link);
  }

  const setActive = (link) => {
    for (const other of links) {
      if (other === link) other.setAttribute('aria-current', 'true');
      else other.removeAttribute('aria-current');
    }
  };

  const observer = new IntersectionObserver((entries) => {
    /* Pick the entry closest to the top of the viewport that is currently
       intersecting — this avoids flicker when two sections overlap. */
    const visible = entries
      .filter(e => e.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (visible.length) setActive(byId.get(visible[0].target));
  }, {
    rootMargin: `-${72 + 16}px 0px -55% 0px`,
    threshold: [0, 0.15, 0.5]
  });

  for (const [section] of byId) observer.observe(section);
}

   Smooth anchor scrolling that respects the fixed navbar
   -------------------------------------------------------------------------- */
function initAnchorScroll() {
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const id = link.hash.slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;

    event.preventDefault();
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    target.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });

    /* Keep the URL shareable without the scroll jump. */
    history.replaceState(null, '', `#${id}`);
    setDrawer(false);
  });
}

   WhatsApp CTAs — wired centrally so the number lives in one place
   -------------------------------------------------------------------------- */
function initWhatsappCtAs() {
  /* The number is read from CONFIG, never inlined here. It used to be
     repeated in ~30 places across two files. */
  for (const link of qsa('[data-wa-cta]')) {
    const message = link.dataset.waMessage || '';
    link.href = message
      ? `${CONFIG.WHATSAPP_BASE}?text=${encodeURIComponent(message)}`
      : CONFIG.WHATSAPP_BASE;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  }
}

export function initNav() {
  nav.hamburger = qs('#hamburger-btn');
  nav.drawer = qs('#mobile-drawer');
  if (!nav.hamburger || !nav.drawer) return;

  nav.hamburger.setAttribute('aria-expanded', 'false');
  nav.hamburger.setAttribute('aria-controls', 'mobile-drawer');
  nav.hamburger.setAttribute('aria-label', 'Toggle navigation menu');
  nav.drawer.setAttribute('aria-hidden', 'true');

  nav.hamburger.addEventListener('click', () => setDrawer(!isOpen()));

  /* Escape closes; Tab is trapped while open. */
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && isOpen()) {
      setDrawer(false);
      nav.hamburger.focus();
    }
    trapFocus(event);
  });

  /* Clicking anywhere outside the drawer closes it. */
  document.addEventListener('click', (event) => {
    if (!isOpen()) return;
    if (nav.drawer.contains(event.target) || nav.hamburger.contains(event.target)) return;
    setDrawer(false);
  });

  /* Reset the drawer if the viewport grows back to desktop. */
  window.matchMedia('(min-width: 861px)').addEventListener?.('change', (e) => {
    if (e.matches) setDrawer(false);
  });

  initScrollSpy();
  initAnchorScroll();
  initWhatsappCtAs();
}

export { setDrawer as setDrawerOpen, isOpen as isDrawerOpen };
