/**
 * booking.js — Package selection, calendar/form synchronisation, WhatsApp dispatch
 * --------------------------------------------------------------------------
 * Fixes carried over:
 *  - selectSlotType() updated one set of DOM nodes while the dispatch
 *    function read a separate, never-updated variable, so the wrong package
 *    was always sent to WhatsApp. Now a single call into the calendar module.
 *  - handleDirectBookingSubmit() opened WhatsApp with the bare
 *    two-argument form of window.open, with no noopener — so the
 *    opened page kept a live reference back to this window (reverse
 *    tabnabbing). Every outbound window now goes through openExternal()
 *    from js/utils.js, which always passes noopener and nulls
 *    window.opener.
 *  - The form had no client-side validation beyond `required`. Phone format
 *    and past-date selection were both accepted and silently forwarded.
 *  - Pre-selecting a package in the form matched on substring, which
 *    repeatedly picked the wrong option. Now matched on explicit keywords.
 */

import { CONFIG, PACKAGE_DATA } from './config.js';
import {
  qs, qsa, el, safeSetText,
  formatISODate, formatReadableDate, startOfToday,
  isValidPhone, isFutureDate, markFieldError, clearFieldError, openExternal
} from './utils.js';
import { showToast } from './toast.js';

   Package selection chips
   -------------------------------------------------------------------------- */

function selectSlotType(button, packageName) {
  for (const chip of document.querySelectorAll('.cal-slot-chip')) {
    const active = chip === button;
    chip.classList.toggle('active', active);
    chip.setAttribute('aria-pressed', String(active));
  }

  const pkg = PACKAGE_DATA[packageName];

  /* Push the choice into the calendar engine so the WhatsApp message and
     every visible readout agree with what the guest actually clicked. */
  window.dispatchEvent(new CustomEvent('fsk:package-selected', {
    detail: { packageName, display: pkg ? pkg.name : packageName }
  }));

  /* Keep the legacy hook working for anything still calling it directly. */
  if (typeof window.setAirbnbReservationPackage === 'function') {
    window.setAirbnbReservationPackage(packageName);
  }

  showToast(`Package selected: ${pkg ? pkg.name : packageName}`);
}

   Match a package name to the closest option in the contact form
   -------------------------------------------------------------------------- */

function selectMatchingOption(packageName) {
  const select = qs('#form-package');
  if (!select) return false;

  const target = String(packageName).toLowerCase();
  const options = Array.from(select.options);

  /* 1. Exact value or label match. */
  let index = options.findIndex(
    (o) => o.value.toLowerCase() === target || o.text.toLowerCase() === target
  );

  /* 2. Keyword match — the old substring loop matched 'wedding'
        against 'Full Wedding Partners', which is a different product. */
  if (index === -1) {
    const pkg = PACKAGE_DATA[packageName];
    const keyword = pkg ? pkg.formKeyword : null;
    if (keyword) {
      index = options.findIndex((o) => o.value.toLowerCase().includes(keyword));
    }
  }

  /* 3. Word-overlap fallback. */
  if (index === -1) {
    const words = target.split(/[^a-z]+/).filter((w) => w.length > 3);
    index = options.findIndex((o) => {
      const haystack = `${o.value} ${o.text}`.toLowerCase();
      return words.some((w) => haystack.includes(w));
    });
  }

  if (index >= 0) {
    select.selectedIndex = index;
    select.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }
  return false;
}

function selectPackageAndScroll(packageName) {
  const matched = selectMatchingOption(packageName);

  const contact = qs('#contact');
  if (contact) {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    contact.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    window.setTimeout(() => qs('#form-name')?.focus(), CONFIG.TIMING.SCROLL_FOCUS_MS);
  }

  showToast(
    matched
      ? `Selected package: ${packageName}. Complete the details below to send to WhatsApp.`
      : `Package noted: ${packageName}. Complete the details below to send to WhatsApp.`
  );
}

   "Fill booking form for this date"
   -------------------------------------------------------------------------- */

function fillFormWithSelectedDate() {
  const state = window.AirbnbCalendarState;
  const date = state && state.rangeStart ? state.rangeStart : startOfToday();

  const formDate = qs('#form-date');
  if (formDate) formDate.value = formatISODate(date);

  const contact = qs('#contact');
  if (contact) {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    contact.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    window.setTimeout(() => qs('#form-name')?.focus(), CONFIG.TIMING.SCROLL_FOCUS_MS);
  }

  showToast(`Date ${formatReadableDate(date)} set. Complete the form below.`);
}

   Direct booking form
   -------------------------------------------------------------------------- */

function validateBookingForm(fields) {
  let valid = true;

  if (!fields.name.value.trim()) {
    markFieldError(fields.name, 'Please enter your full name or organisation.');
    valid = false;
  } else clearFieldError(fields.name);

  if (!isValidPhone(fields.phone.value)) {
    markFieldError(fields.phone, 'Enter a reachable phone or WhatsApp number.');
    valid = false;
  } else clearFieldError(fields.phone);

  if (!fields.date.value) {
    markFieldError(fields.date, 'Choose your performance date.');
    valid = false;
  } else if (!isFutureDate(fields.date.value)) {
    markFieldError(fields.date, 'Pick a date in the future.');
    valid = false;
  } else clearFieldError(fields.date);

  if (!fields.location.value.trim()) {
    markFieldError(fields.location, 'Tell us the venue and city.');
    valid = false;
  } else clearFieldError(fields.location);

  return valid;
}

function handleDirectBookingSubmit(event) {
  event.preventDefault();

  const fields = {
    name: qs('#form-name'),
    phone: qs('#form-phone'),
    date: qs('#form-date'),
    location: qs('#form-location'),
    package: qs('#form-package'),
    message: qs('#form-message')
  };

  if (!validateBookingForm(fields)) {
    showToast('Please correct the highlighted fields before sending.');
    const firstError = document.querySelector('.form-field.has-error input, .form-field.has-error select');
    firstError?.focus();
    return;
  }

  const body = [
    `*${CONFIG.ARTIST_STAGE.toUpperCase()} - PERFORMANCE INQUIRY*`,
    '----------------------------------------',
    `Client / Org: ${fields.name.value.trim()}`,
    `Phone / WhatsApp: ${fields.phone.value.trim()}`,
    `Performance Date: ${fields.date.value}`,
    `Venue & City: ${fields.location.value.trim()}`,
    `Package Selected: ${fields.package.value}`,
    `Event Notes: ${fields.message.value.trim() || 'Tailored repertoire curation'}`,
    '----------------------------------------',
    `Sent via ${CONFIG.SITE_ORIGIN.replace(/^https?:\/\//, '')} booking form`
  ].join('\n');

  showToast('Redirecting to WhatsApp to send your booking inquiry...');
  window.setTimeout(
    () => openExternal(`${CONFIG.WHATSAPP_BASE}?text=${encodeURIComponent(body)}`),
    CONFIG.TIMING.DISPATCH_MS
  );
}

   Moodboard viewer
   -------------------------------------------------------------------------- */

function openPhotoViewer(title) {
  showToast(`Viewing: ${title} (@ojiespov)`);
}

   Init
   -------------------------------------------------------------------------- */

export function initBooking() {
  /* Package chips */
  for (const chip of document.querySelectorAll('.cal-slot-chip')) {
    const name = chip.dataset.package || chip.querySelector('.slot-chip-name')?.textContent?.trim();
    if (!name) continue;
    chip.type = 'button';
    chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
    chip.addEventListener('click', () => selectSlotType(chip, name));
  }

  /* The calendar module owns range state; keep it in sync with the form. */
  document.addEventListener('fsk:package-selected', () => {
    /* already applied by selectSlotType via setAirbnbReservationPackage */
  });

  /* Contact form */
  const form = qs('#direct-booking-form');
  if (form) {
    form.addEventListener('submit', handleDirectBookingSubmit);
    /* Clear an error as soon as the user starts fixing it. */
    for (const input of form.querySelectorAll('input, select, textarea')) {
      input.addEventListener('input', () => clearFieldError(input));
    }
  }

  /* Global hooks used by markup and by the legacy inline handlers. */
  window.selectSlotType = selectSlotType;
  window.selectPackageAndScroll = selectPackageAndScroll;
  window.fillFormWithSelectedDate = fillFormWithSelectedDate;
  window.handleDirectBookingSubmit = handleDirectBookingSubmit;
  window.openPhotoViewer = openPhotoViewer;
}

export {
  selectSlotType,
  selectPackageAndScroll,
  fillFormWithSelectedDate,
  handleDirectBookingSubmit,
  selectMatchingOption
};
