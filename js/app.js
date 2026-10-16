/**
 * app.js — Application entry point
 * --------------------------------------------------------------------------
 * Loaded as <script type="module"> so the browser defers execution until the
 * DOM is parsed and each import can be cached independently. That single
 * change removes a render-blocking script from the critical path.
 *
 * Every module self-initialises exactly once, and every failure is caught
 * and logged rather than silently killing the rest of the boot sequence.
 * The duplicated-entry guard is deliberate: a stale service worker or a
 * double <script> tag must not double-bind handlers.
 *
 * All markup interactivity is wired through data-action attributes and
 * delegated listeners (see js/actions.js). There are no inline handlers
 * anywhere on the page, which is what makes a strict CSP possible.
 */

import { initActions, registerAction } from './actions.js';
import { qs } from './utils.js';
import { initNav } from './nav.js';
import { initHero } from './hero.js';
import { initVideos } from './videos.js';
import { initAirbnbCalendar } from './airbnb-calendar.js';
import { initBooking } from './booking.js';
import { initPortal } from './portal.js';

const booted = new WeakSet();

function boot(name, initialiser) {
  if (booted.has(initialiser)) return;
  booted.add(initialiser);
  try {
    initialiser();
  } catch (error) {
    /* One broken module must not take the whole page down with it. */
    console.error(`[Frederic Sax Ke] ${name} failed to initialise`, error);
  }
}

/** Map every data-action in the markup to a handler. */
function registerActions() {
  /* Calendar */
  registerAction('set-mode', (element) => window.setAirbnbBookingMode(element.dataset.mode));
  registerAction('set-tolerance', (element) => window.setAirbnbTolerance(element, element.dataset.tolerance));
  registerAction('clear-dates', () => window.clearAirbnbDates());
  registerAction('open-slot-modal', () => window.openSlotChangeModal());
  registerAction('close-slot-modal', (element) => {
    /* Only the backdrop closes on a direct click; callers use the button. */
    if (element.dataset.backdrop === 'true') {
      window.closeSlotChangeModal();
      return;
    }
    window.closeSlotChangeModal();
  });
  registerAction('select-slot', (element) => {
    window.selectPerformanceSlot(element.dataset.slot, element.dataset.label, element.dataset.package);
  });
  registerAction('reserve', (element) => {
    window.dispatchAirbnbReservationWhatsApp(element.dataset.simulate === 'true');
  });
  registerAction('fill-form-date', () => window.fillFormWithSelectedDate());

  /* Booking */
  registerAction('select-package', (element) => window.selectPackageAndScroll(element.dataset.package));
  registerAction('open-photo', (element) => window.openPhotoViewer(element.dataset.title));

  /* Portal */
  registerAction('download-contract', () => window.downloadSampleContract());
  registerAction('print-invoice', () => window.printInvoice());

  /* Rate card page (dynamically imported below so index.html never
     downloads the pricing page's JavaScript) */
  registerAction('set-currency', (element) => window.setCurrency?.(element.dataset.currency));
  registerAction('open-booking-modal', (element) => window.openBookingModal?.(element.dataset.package));
  registerAction('close-booking-modal', () => window.closeBookingModal?.());
  registerAction('print-ratecard', () => window.printRateCard?.());
}

/**
 * Backdrop dismissal for both modals.
 * Listener runs at the document level and checks the closest modal, so
 * clicks that start inside the card and drag out do not dismiss it.
 */
function initModalBackdrops() {
  document.addEventListener('click', (event) => {
    if (event.target !== event.currentTarget) return;

    for (const id of ['bnb-slot-modal', 'booking-modal-overlay']) {
      const overlay = document.getElementById(id);
      if (!overlay) continue;
      if (overlay.dataset.backdrop === 'true' && event.target === overlay) {
        if (id === 'bnb-slot-modal') window.closeSlotChangeModal?.();
        else window.closeBookingModal?.();
        return;
      }
    }
  });
}

function initApp() {
  document.documentElement.classList.add('js-ready');

  registerActions();
  boot('actions', initActions);
  initModalBackdrops();

  boot('nav', initNav);
  boot('hero', initHero);
  boot('videos', initVideos);
  boot('airbnb-calendar', initAirbnbCalendar);
  boot('booking', initBooking);
  boot('portal', initPortal);

  /* The rate card page needs js/rate-card.js. It is code-split so a visitor
     on the portfolio page never downloads it. */
  if (qs('#booking-modal-overlay') || qs('.btn-table-inquire') || qs('.curr-btn')) {
    import('./rate-card.js')
      .then(({ initRateCard }) => boot('rate-card', initRateCard))
      .catch((error) => console.error('[Frederic Sax Ke] rate-card failed to load', error));
  }

  /* Flip the non-render-blocking font stylesheet on. */
  import('./fonts.js').catch(() => {});

  document.documentElement.classList.add('js-ready-complete');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp, { once: true });
} else {
  initApp();
}
