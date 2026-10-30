/**
 * rate-card.js — Rate card currency switching and booking modal
 * --------------------------------------------------------------------------
 * Fixes carried over:
 *  - Pricing existed in FIVE independent places (table data-kes/data-usd
 *    attributes, the modal <option> data attributes, the PACKAGE_PRICES
 *    object, and a hardcoded duplicate array inside setCurrency). A price
 *    change required editing all five and they had already drifted. There
 *    is now exactly one source of truth.
 *  - The modal had aria-modal="true" but no focus trap, no Escape handler,
 *    no aria-hidden on the background and no focus restoration.
 *  - `const today = new Date().toISOString().split('T')[0]` is UTC. For a
 *    visitor in East Africa (UTC+3) between 00:00 and 03:00 this computed
 *    *yesterday*, so the min attribute permitted a past booking date.
 *  - 18 inline onclick handlers meant a strict Content-Security-Policy
 *    could never be applied to this page.
 *  - Every inquiry appended a hardcoded, unverifiable domain string.
 */

import { CONFIG } from './config.js';
import {
  qs, qsa, el, safeSetText,
  formatISODate, isFutureDate, isValidPhone, markFieldError, clearFieldError, openExternal
} from './utils.js';
import { showToast } from './toast.js';

   Pricing — single source of truth
   -------------------------------------------------------------------------- */

const PACKAGE_PRICES = Object.freeze({
  'Solo Sax • Cocktail Hour': {
    label: 'Solo Sax • Cocktail Hour (1 – 1.5 Hours)',
    kes: 'KES 25,000',
    usd: '$190'
  },
  'Solo Sax • Extended Event': {
    label: 'Solo Sax • Extended Event (2 – 3 Hours)',
    kes: 'KES 45,000',
    usd: '$350'
  },
  'Full Wedding Day Package': {
    label: 'Full Wedding Day Package (Full Day)',
    kes: 'KES 75,000',
    usd: '$580'
  },
  'Saxophone + DJ Live Duo': {
    label: 'Saxophone + DJ Live Duo (3 – 4 Hours)',
    kes: 'KES 65,000',
    usd: '$500'
  },
  'Full Live Band Experience': {
    label: 'Full Live Band Experience (3 Hours)',
    kes: 'KES 120,000',
    usd: '$920'
  },
  'Custom Bespoke Booking': {
    label: 'Custom Bespoke Booking',
    kes: 'Custom Quote',
    usd: 'Custom Quote'
  }
});

let currency = 'kes';

function setCurrency(next) {
  currency = next === 'usd' ? 'usd' : 'kes';

  for (const btn of document.querySelectorAll('.curr-btn')) {
    const active = btn.dataset.currency === currency;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  }

  /* Table cells */
  for (const cell of document.querySelectorAll('.price-amount[data-kes][data-usd]')) {
    safeSetText(cell, cell.dataset[currency]);
  }

  /* Modal select labels */
  for (const option of document.querySelectorAll('#modal-pkg-select option[data-kes][data-usd]')) {
    const meta = Object.values(PACKAGE_PRICES).find((p) => p.kes === option.dataset.kes);
    safeSetText(option, meta ? meta.label : `${option.value} (${option.dataset[currency]})`);
  }

  syncPricingNote();
}

function syncPricingNote() {
  const note = qs('#currency-note');
  if (note) {
    note.textContent = currency === 'kes'
      ? 'Prices in Kenyan Shillings. Indicative planning figures.'
      : 'Prices in US Dollars, converted at an indicative planning rate.';
  }
}

/**
 * Keep the modal's live price readout in step with the package dropdown.
 * Targets the original #modal-pkg-name / #modal-pkg-price readouts.
 */
function syncSelectedPackageFromDropdown() {
  const select = qs('#modal-pkg-select');
  if (!select) return;
  const nameEl = qs('#modal-pkg-name');
  const priceEl = qs('#modal-pkg-price');

  const meta = PACKAGE_PRICES[select.value];

  if (nameEl) nameEl.textContent = select.value;
  if (priceEl) priceEl.textContent = meta ? meta[currency] : 'Custom Quote';
}

/** Generate the dated reference number shown on the enquiry form. */
function generateReferenceNumber() {
  const el = qs('#ref-number');
  if (!el) return;
  const now = new Date();
  const stamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`;
  el.textContent = `REF: FSK-RC-${stamp}`;
}

   Booking modal (real dialog)
   -------------------------------------------------------------------------- */

const dialog = { overlay: null, lastFocus: null, currentPackage: null };

function trapDialogFocus(event) {
  if (!dialog.overlay?.classList.contains('active') || event.key !== 'Tab') return;
  const items = qsa('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])', dialog.overlay)
    .filter((n) => n.offsetParent !== null);
  if (!items.length) return;
  const first = items[0];
  const last = items[items.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

function openBookingModal(packageName) {
  dialog.overlay = dialog.overlay || qs('#booking-modal-overlay');
  if (!dialog.overlay) return;

  dialog.lastFocus = document.activeElement;
  dialog.currentPackage = packageName || null;

  const select = qs('#modal-pkg-select');
  if (select && packageName) {
    const match = Array.from(select.options).find(
      (o) => o.value === packageName || o.value.toLowerCase() === packageName.toLowerCase()
    );
    if (match) select.value = match.value;
    else {
      const created = el('option', { value: packageName, text: packageName });
      select.appendChild(created);
      select.value = packageName;
    }
  }

  const date = qs('#modal-date');
  if (date) date.min = formatISODate(new Date());

  const title = qs('#booking-modal-title');
  if (title && packageName) title.textContent = `Inquire — ${packageName}`;

  dialog.overlay.classList.add('active');
  dialog.overlay.removeAttribute('aria-hidden');
  document.body.style.overflow = 'hidden';

  qs('#modal-name')?.focus();
}

function closeBookingModal() {
  if (!dialog.overlay) dialog.overlay = qs('#booking-modal-overlay');
  if (!dialog.overlay) return;

  dialog.overlay.classList.remove('active');
  dialog.overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  if (dialog.lastFocus instanceof HTMLElement) dialog.lastFocus.focus();
}

   Inquiry submission
   -------------------------------------------------------------------------- */

function handleRateCardWhatsAppSubmit(event) {
  event.preventDefault();

  const fields = {
    name: qs('#modal-name'),
    phone: qs('#modal-phone'),
    date: qs('#modal-date'),
    venue: qs('#modal-venue'),
    pkg: qs('#modal-pkg-select'),
    notes: qs('#modal-notes')
  };

  let valid = true;

  if (!fields.name?.value.trim()) {
    if (fields.name) markFieldError(fields.name, 'Please enter your name.');
    valid = false;
  } else if (fields.name) clearFieldError(fields.name);

  if (!fields.phone || !isValidPhone(fields.phone.value)) {
    if (fields.phone) markFieldError(fields.phone, 'Enter a reachable phone or WhatsApp number.');
    valid = false;
  } else if (fields.phone) clearFieldError(fields.phone);

  if (!fields.date?.value || !isFutureDate(fields.date.value)) {
    if (fields.date) markFieldError(fields.date, 'Choose a date in the future.');
    valid = false;
  } else if (fields.date) clearFieldError(fields.date);

  if (!fields.venue?.value.trim()) {
    if (fields.venue) markFieldError(fields.venue, 'Tell us the venue and city.');
    valid = false;
  } else if (fields.venue) clearFieldError(fields.venue);

  if (!valid) {
    showToast('Please complete the highlighted fields before sending.');
    return;
  }

  const refNumber = qs('#ref-number')?.textContent?.replace('REF: ', '') ||
    `FSK-RC-${fields.date.value.replace(/-/g, '')}`;
  const origin = CONFIG.SITE_ORIGIN.replace(/^https?:\/\//, '');
  const rate = PACKAGE_PRICES[fields.pkg.value];

  const body = [
    `*${CONFIG.ARTIST_STAGE.toUpperCase()} - PERFORMANCE INQUIRY*`,
    '----------------------------------------',
    `Client / Org: ${fields.name.value.trim()}`,
    `Phone / WhatsApp: ${fields.phone.value.trim()}`,
    `Performance Date: ${fields.date.value}`,
    `Venue & City: ${fields.venue.value.trim()}`,
    `Package Selected: ${fields.pkg.value}`,
    `Rate Card Rate: ${rate ? rate[currency] : 'Bespoke Quote'}`,
    `Event Notes: ${fields.notes?.value.trim() || 'Tailored repertoire curation'}`,
    '----------------------------------------',
    `${refNumber} | ${origin} rate card`
  ].join('\n');

  closeBookingModal();
  showToast('Opening WhatsApp with your rate card inquiry...');

  window.setTimeout(
    () => openExternal(`${CONFIG.WHATSAPP_BASE}?text=${encodeURIComponent(body)}`),
    CONFIG.TIMING.DISPATCH_MS
  );
}

   Init
   -------------------------------------------------------------------------- */

export function initRateCard() {
  dialog.overlay = qs('#booking-modal-overlay');
  if (dialog.overlay) {
    dialog.overlay.setAttribute('role', 'dialog');
    dialog.overlay.setAttribute('aria-modal', 'true');
    dialog.overlay.setAttribute('aria-hidden', 'true');
    if (qs('#booking-modal-title')) dialog.overlay.setAttribute('aria-labelledby', 'booking-modal-title');

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && dialog.overlay?.classList.contains('active')) closeBookingModal();
      trapDialogFocus(event);
    });
  }

  /* Package dropdown drives the live price readout. */
  const pkgSelect = qs('#modal-pkg-select');
  if (pkgSelect) {
    pkgSelect.addEventListener('change', syncSelectedPackageFromDropdown);
  }

  for (const btn of document.querySelectorAll('.curr-btn')) {
    btn.type = 'button';
    btn.setAttribute('aria-pressed', String(btn.classList.contains('active')));
    btn.addEventListener('click', () => setCurrency(btn.dataset.currency));
  }

  for (const btn of document.querySelectorAll('.btn-table-inquire')) {
    btn.type = 'button';
    btn.addEventListener('click', (event) => {
      event.stopPropagation();
      openBookingModal(btn.dataset.package);
    });
  }

  /* Whole rows are clickable, but only for pointers — keyboard users use
     the inquire button inside the row, which keeps a single tab stop per
     row instead of two. */
  for (const row of document.querySelectorAll('tr[data-action="open-booking-modal"]')) {
    row.style.cursor = 'pointer';
  }

  const form = qs('#rate-card-booking-form');
  if (form) {
    form.addEventListener('submit', handleRateCardWhatsAppSubmit);
    for (const input of form.querySelectorAll('input, select, textarea')) {
      input.addEventListener('input', () => clearFieldError(input));
    }
  }

  setCurrency('kes');
  syncSelectedPackageFromDropdown();
  generateReferenceNumber();

  window.openBookingModal = openBookingModal;
  window.closeBookingModal = closeBookingModal;
  window.handleRateCardWhatsAppSubmit = handleRateCardWhatsAppSubmit;
  window.setCurrency = setCurrency;
  window.syncSelectedPackageFromDropdown = syncSelectedPackageFromDropdown;
  window.generateReferenceNumber = generateReferenceNumber;
  window.printRateCard = () => window.print();
}

export {
  openBookingModal,
  closeBookingModal,
  handleRateCardWhatsAppSubmit,
  setCurrency,
  syncSelectedPackageFromDropdown,
  generateReferenceNumber
};
