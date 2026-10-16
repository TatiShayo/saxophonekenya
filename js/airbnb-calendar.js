/**
 * airbnb-calendar.js — Airbnb-style continuous calendar & reservation engine
 * --------------------------------------------------------------------------
 * Module rewrite. The bugs fixed here are material:
 *
 *  1. HARD-CODED "TODAY". The engine declared
 *         viewYear: 2026, viewMonth: 9, today: new Date(2026, 9, 7)
 *     with a fixed rangeStart of 8 October and a fixed 2-month window. The
 *     moment November arrived, every date on screen was already "past" and
 *     the calendar silently showed a dead month. The engine now derives its
 *     whole timeline from the real current date.
 *
 *  2. RANGES COULD SPAN BOOKED DATES. handleDateClick accepted any end date
 *     later than the start, including ones containing held dates. A guest
 *     could "reserve" 8–16 October when the 12th, 13th, 14th, 15th and 16th
 *     were all marked unavailable. Selection now validates the whole range.
 *
 *  3. NO KEYBOARD ACCESS. Day cells were <div onclick>. A keyboard user
 *     could not open or use the calendar at all. They are now focusable
 *     gridcells with arrow-key navigation, Home/End and Enter/Space.
 *
 *  4. MODAL HAD NO FOCUS TRAP. openSlotChangeModal/closeSlotChangeModal
 *     only toggled a class. Tab walked into the page behind the overlay and
 *     Escape did nothing. Now a proper modal dialog.
 *
 *  5. XSS / TABNABBING. User-visible text used to be written into
 *     innerHTML sinks, and the WhatsApp window was opened with the
 *     bare two-argument form of window.open, without noopener.
 *     Both fixed — textContent, and every outbound window now goes
 *     through the openExternal() helper in js/utils.js, which always
 *     passes noopener and nulls window.opener.
 */

import { CONFIG, PACKAGE_DATA } from './config.js';
import {
  qs, qsa, el, safeSetText,
  formatISODate, formatRangeDisplay, mondayFirstIndex, daysInMonth,
  isSameDay, startOfToday, prefersReducedMotion, openExternal
} from './utils.js';
import { showToast } from './toast.js';

/* ==========================================================================
   State
   ========================================================================== */

const STATE = {
  /* Always anchored to the visitor's real "today" and current month. */
  today: startOfToday(),
  viewYear: startOfToday().getFullYear(),
  viewMonth: startOfToday().getMonth(),
  monthsCount: CONFIG.MONTHS_TO_RENDER,

  rangeStart: null,
  rangeEnd: null,

  bookingMode: 'dates',
  flexTolerance: 'exact',

  selectedSlot: {
    name: 'Evening Set (18:00 – 22:00)',
    label: 'Evening Reception & Cocktail',
    package: 'Full Wedding Day Package'
  },

  bookedDates: [...CONFIG.BOOKED_DATES],
  focusDate: null
};

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

/* ==========================================================================
   Availability
   ========================================================================== */

function isDateUnavailable(date) {
  const iso = formatISODate(date);
  if (date < STATE.today) return true;
  if (STATE.bookedDates.includes(iso)) return true;
  return false;
}

/** True when every day in [start, end] is bookable. */
function rangeIsClean(start, end) {
  if (!start || !end) return false;
  const cursor = new Date(start);
  while (cursor <= end) {
    if (isDateUnavailable(cursor)) return false;
    cursor.setDate(cursor.getDate() + 1);
  }
  return true;
}

function isDateInRange(date) {
  if (!STATE.rangeStart || !STATE.rangeEnd) return false;
  const t = date.getTime();
  return t > STATE.rangeStart.getTime() && t < STATE.rangeEnd.getTime();
}

/* ==========================================================================
   Rendering
   ========================================================================== */

const STREAM_ID = 'bnb-calendar-stream';

function buildMonthSection(year, month) {
  const section = el('div', { class: 'bnb-month-section', 'data-month': `${year}-${String(month + 1).padStart(2, '0')}` });

  section.appendChild(el('div', {
    class: 'bnb-month-title',
    text: `${MONTH_NAMES[month]} ${year}`
  }));

  const grid = el('div', {
    class: 'bnb-days-grid',
    role: 'grid',
    'aria-label': `${MONTH_NAMES[month]} ${year} performance dates`
  });

  const offset = mondayFirstIndex(year, month, 1);
  for (let i = 0; i < offset; i++) {
    grid.appendChild(el('div', { class: 'bnb-day-cell empty', 'aria-hidden': 'true' }));
  }

  const total = daysInMonth(year, month);
  for (let day = 1; day <= total; day++) {
    grid.appendChild(buildDayCell(new Date(year, month, day)));
  }

  section.appendChild(grid);
  return section;
}

function buildDayCell(date) {
  const cell = el('div', { class: 'bnb-day-cell' });
  cell.appendChild(el('span', { class: 'bnb-day-num', text: String(date.getDate()) }));

  const iso = formatISODate(date);
  const label = formatRangeDisplay(date, date).replace(/\s/g, ' ');
  cell.dataset.date = iso;

  const unavailable = isDateUnavailable(date);

  if (unavailable) {
    cell.classList.add('struck');
    /* aria-disabled rather than `disabled`: the cell stays in the grid so
       screen-reader users understand the structure, but is clearly inert. */
    cell.setAttribute('aria-disabled', 'true');
    cell.setAttribute('title', 'Date unavailable / held');
    cell.setAttribute('role', 'gridcell');
    cell.setAttribute('aria-label', `${label} — unavailable`);
    cell.tabIndex = -1;
    return cell;
  }

  const isStart = isSameDay(date, STATE.rangeStart);
  const isEnd = isSameDay(date, STATE.rangeEnd);
  const inRange = isDateInRange(date);
  const isToday = isSameDay(date, STATE.today);

  if (isStart && isEnd) cell.classList.add('single-selected');
  else if (isStart) cell.classList.add('range-start');
  else if (isEnd) cell.classList.add('range-end');
  else if (inRange) cell.classList.add('in-range');

  if (isToday) cell.classList.add('today');

  cell.setAttribute('role', 'gridcell');
  cell.setAttribute('aria-selected', String(isStart || isEnd));
  cell.setAttribute('tabindex', '0');
  cell.setAttribute('aria-label', `${label} — open for booking${isToday ? ' (today)' : ''}`);

  cell.addEventListener('click', () => handleDateClick(date));
  cell.addEventListener('keydown', (event) => handleDayKeydown(event, date));

  return cell;
}

function renderCalendarStream() {
  const stream = document.getElementById(STREAM_ID);
  if (!stream) return;

  stream.innerHTML = '';

  for (let i = 0; i < STATE.monthsCount; i++) {
    let month = STATE.viewMonth + i;
    let year = STATE.viewYear;
    if (month > 11) { month -= 12; year += 1; }
    stream.appendChild(buildMonthSection(year, month));
  }

  /* Default the selection to the first bookable day at/after today, rather
     than the stale hard-coded 8 October. */
  if (!STATE.rangeStart || isDateUnavailable(STATE.rangeStart)) {
    STATE.rangeStart = firstAvailableFrom(STATE.today);
    STATE.rangeEnd = null;
  }

  syncUIWithSelection();
}

function firstAvailableFrom(date) {
  const cursor = new Date(date);
  for (let i = 0; i < 60; i++) {
    if (!isDateUnavailable(cursor)) return cursor;
    cursor.setDate(cursor.getDate() + 1);
  }
  return new Date(date);
}

/* ==========================================================================
   Keyboard navigation
   ========================================================================== */

function focusDayCell(date) {
  const cell = document.querySelector(`.bnb-day-cell[data-date="${formatISODate(date)}"]`);
  if (cell && cell.getAttribute('aria-disabled') !== 'true') {
    cell.focus();
    STATE.focusDate = date;
  }
}

function handleDayKeydown(event, date) {
  const step = (days) => {
    const next = new Date(date);
    next.setDate(next.getDate() + days);
    focusDayCell(next);
  };

  switch (event.key) {
    case 'ArrowRight': event.preventDefault(); step(1); break;
    case 'ArrowLeft':  event.preventDefault(); step(-1); break;
    case 'ArrowDown':  event.preventDefault(); step(7); break;
    case 'ArrowUp':    event.preventDefault(); step(-7); break;
    case 'Home':       event.preventDefault(); focusDayCell(new Date(date.getFullYear(), date.getMonth(), 1)); break;
    case 'End': {
      event.preventDefault();
      focusDayCell(new Date(date.getFullYear(), date.getMonth() + 1, 0));
      break;
    }
    case 'PageUp':   event.preventDefault(); shiftMonth(-1); break;
    case 'PageDown': event.preventDefault(); shiftMonth(1); break;
    case 'Enter':
    case ' ':
      event.preventDefault();
      handleDateClick(date);
      break;
    default: break;
  }
}

function shiftMonth(delta) {
  STATE.viewMonth += delta;
  if (STATE.viewMonth > 11) { STATE.viewMonth = 0; STATE.viewYear += 1; }
  if (STATE.viewMonth < 0) { STATE.viewMonth = 11; STATE.viewYear -= 1; }
  renderCalendarStream();
}

/* ==========================================================================
   Selection
   ========================================================================== */

function handleDateClick(clicked) {
  const target = new Date(clicked);
  target.setHours(0, 0, 0, 0);

  if (!STATE.rangeStart || STATE.rangeEnd) {
    /* Starting a fresh selection. */
    if (isDateUnavailable(target)) {
      showToast('That date is already held.');
      return;
    }
    STATE.rangeStart = target;
    STATE.rangeEnd = null;
  } else {
    /* Completing a range. */
    if (target.getTime() < STATE.rangeStart.getTime()) {
      STATE.rangeStart = target;
      STATE.rangeEnd = null;
    } else if (isSameDay(target, STATE.rangeStart)) {
      STATE.rangeEnd = target;                 /* single-day range */
    } else if (!rangeIsClean(STATE.rangeStart, target)) {
      showToast('That range includes held dates. Please pick a clear run of days.');
      return;
    } else {
      STATE.rangeEnd = target;
    }
  }

  STATE.focusDate = target;
  renderCalendarStream();
}

function syncUIWithSelection() {
  const rangeText = formatRangeDisplay(STATE.rangeStart, STATE.rangeEnd);

  safeSetText(qs('#cal-selected-date-text'), rangeText);

  const formDate = qs('#form-date');
  if (formDate && STATE.rangeStart) formDate.value = formatISODate(STATE.rangeStart);

  const summary = qs('#bnb-selection-summary');
  if (summary) {
    const flexLabel = STATE.flexTolerance !== 'exact' ? ` (± ${STATE.flexTolerance} days)` : '';
    summary.textContent = `${rangeText}${flexLabel} • ${STATE.selectedSlot.name}`;
  }

  const bookBtn = qs('#cal-book-btn-text');
  if (bookBtn && STATE.rangeStart) {
    const month = MONTH_NAMES[STATE.rangeStart.getMonth()].slice(0, 3);
    bookBtn.textContent = `Reserve ${STATE.rangeStart.getDate()} ${month} on WhatsApp`;
  }

  /* Announce selection changes to assistive tech. */
  const live = qs('#bnb-live-region');
  if (live) live.textContent = `Selected ${rangeText}`;
}

/* ==========================================================================
   Public API (kept window-global for compatibility)
   ========================================================================== */

window.setAirbnbBookingMode = function setAirbnbBookingMode(mode) {
  STATE.bookingMode = mode;

  const btnDates = qs('#bnb-mode-dates');
  const btnFlex = qs('#bnb-mode-flexible');
  const flexSection = qs('#bnb-flex-section');

  btnDates?.classList.toggle('active', mode === 'dates');
  btnDates?.setAttribute('aria-selected', String(mode === 'dates'));
  btnFlex?.classList.toggle('active', mode === 'flexible');
  btnFlex?.setAttribute('aria-selected', String(mode === 'flexible'));

  /* Toggle the `hidden` attribute rather than an inline style so the page
     carries no inline style at all and the CSP can stay strict. */
  if (flexSection) flexSection.hidden = mode !== 'flexible';

  syncUIWithSelection();
};

window.setAirbnbTolerance = function setAirbnbTolerance(btn, tolerance) {
  STATE.flexTolerance = tolerance;
  for (const chip of document.querySelectorAll('.bnb-flex-chip')) {
    const active = chip === btn;
    chip.classList.toggle('active', active);
    chip.setAttribute('aria-pressed', String(active));
  }
  syncUIWithSelection();
};

window.clearAirbnbDates = function clearAirbnbDates() {
  STATE.rangeStart = null;
  STATE.rangeEnd = null;
  renderCalendarStream();
  showToast('Dates reset. Select your preferred performance date.');
};

/* ---- Performance slot modal (now a real dialog) ------------------------- */

const modal = {
  overlay: null,
  lastFocus: null
};

function trapModalFocus(event) {
  if (!modal.overlay?.classList.contains('active') || event.key !== 'Tab') return;
  const items = qsa('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])', modal.overlay)
    .filter(n => n.offsetParent !== null);
  if (!items.length) return;
  const first = items[0];
  const last = items[items.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

window.openSlotChangeModal = function openSlotChangeModal() {
  if (!modal.overlay) modal.overlay = qs('#bnb-slot-modal');
  if (!modal.overlay) return;

  modal.lastFocus = document.activeElement;
  modal.overlay.classList.add('active');
  modal.overlay.removeAttribute('aria-hidden');
  document.body.style.overflow = 'hidden';

  const first = modal.overlay.querySelector('.bnb-slot-opt') || modal.overlay.querySelector('button');
  first?.focus();
};

window.closeSlotChangeModal = function closeSlotChangeModal() {
  if (!modal.overlay) modal.overlay = qs('#bnb-slot-modal');
  if (!modal.overlay) return;

  modal.overlay.classList.remove('active');
  modal.overlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  if (modal.lastFocus instanceof HTMLElement) modal.lastFocus.focus();
};

window.selectPerformanceSlot = function selectPerformanceSlot(slotName, slotLabel, slotPackage) {
  STATE.selectedSlot = { name: slotName, label: slotLabel, package: slotPackage };

  safeSetText(qs('#bnb-slot-bar-val'), slotName);
  safeSetText(qs('#airbnb-selected-pkg-display'), slotPackage);
  safeSetText(qs('#airbnb-item-name'), slotPackage);

  for (const opt of document.querySelectorAll('.bnb-slot-opt')) {
    const selected = opt.dataset.slot === slotName;
    opt.classList.toggle('selected', selected);
    opt.setAttribute('aria-pressed', String(selected));
  }

  closeSlotChangeModal();
  syncUIWithSelection();
  showToast(`Performance slot updated: ${slotLabel}`);
};

/**
 * Exposed so the package chips in the reservation card can drive the
 * WhatsApp message. Previously the chips updated one element while the
 * dispatch function read a completely separate, never-updated variable —
 * so selecting "Ceremony Sax Only" then hitting Reserve still sent
 * "Full Wedding Day Package" to WhatsApp.
 */
window.setAirbnbReservationPackage = function setAirbnbReservationPackage(packageName) {
  const pkg = PACKAGE_DATA[packageName];
  if (!pkg) {
    STATE.selectedSlot.package = packageName;
    safeSetText(qs('#airbnb-item-name'), packageName);
    safeSetText(qs('#airbnb-selected-pkg-display'), packageName);
    syncUIWithSelection();
    return;
  }
  STATE.selectedSlot.package = pkg.name;
  safeSetText(qs('#airbnb-item-name'), pkg.name);
  safeSetText(qs('#airbnb-selected-pkg-display'), pkg.name);
  syncUIWithSelection();
};

/* ---- WhatsApp dispatch -------------------------------------------------- */

window.dispatchAirbnbReservationWhatsApp = function dispatchAirbnbReservationWhatsApp(isSimulation = false) {
  const start = STATE.rangeStart || STATE.today;
  const end = STATE.rangeEnd || start;
  const dateRangeStr = formatRangeDisplay(start, end);
  const flexText = STATE.flexTolerance !== 'exact' ? `± ${STATE.flexTolerance} days` : 'Exact dates';
  const pkgName = STATE.selectedSlot.package || 'Full Wedding Day Package';
  const slotName = STATE.selectedSlot.name;
  const refNum = `${CONFIG.REF_PREFIX}${start.getFullYear()}${String(start.getMonth() + 1).padStart(2, '0')}${String(start.getDate()).padStart(2, '0')}`;

  let message;

  if (isSimulation) {
    message =
      `⚠️ [TEST BOOKING SIMULATION]\n` +
      `----------------------------------------\n` +
      `*AUTOMATED SYSTEM VERIFICATION TEST*\n` +
      `Note: This is a simulated booking test to verify WhatsApp routing.\n` +
      `----------------------------------------\n` +
      `Client / Tester: Automated System Verification\n` +
      `Performance Dates: ${dateRangeStr}\n` +
      `Tolerance: ${flexText}\n` +
      `Performance Slot: ${slotName}\n` +
      `Package Requested: ${pkgName}\n` +
      `Venue / Location: Nairobi & Surrounds (Simulated)\n` +
      `----------------------------------------\n` +
      `STATUS: TEST SIMULATION VERIFIED\n` +
      `Ref: ${refNum} | ${CONFIG.SITE_ORIGIN.replace(/^https?:\/\//, '')}`;
  } else {
    message =
      `*FREDERIC SAX KE - PERFORMANCE RESERVATION*\n` +
      `----------------------------------------\n` +
      `Performance Dates: ${dateRangeStr}\n` +
      `Date Flexibility: ${flexText}\n` +
      `Performance Slot: ${slotName}\n` +
      `Package: ${pkgName}\n` +
      `Location: Nairobi & East Africa\n` +
      `----------------------------------------\n` +
      `Please confirm date availability and performance hold.\n` +
      `Ref: ${refNum} | ${CONFIG.SITE_ORIGIN.replace(/^https?:\/\//, '')}`;
  }

  const waUrl = `${CONFIG.WHATSAPP_BASE}?text=${encodeURIComponent(message)}`;

  showToast(
    isSimulation
      ? 'Dispatching [TEST BOOKING SIMULATION] to WhatsApp...'
      : 'Connecting directly to Frederic on WhatsApp...'
  );

  window.setTimeout(() => openExternal(waUrl), CONFIG.TIMING.DISPATCH_MS);
};

/* ==========================================================================
   Month navigation
   ========================================================================== */

window.calPrevMonth = () => shiftMonth(-1);
window.calNextMonth = () => shiftMonth(1);

/* ==========================================================================
   Init
   ========================================================================== */

export function initAirbnbCalendar() {
  modal.overlay = qs('#bnb-slot-modal');
  if (!modal.overlay) return;

  /* Wire the modal's ARIA contract now that we have the node. */
  modal.overlay.setAttribute('role', 'dialog');
  modal.overlay.setAttribute('aria-modal', 'true');
  modal.overlay.setAttribute('aria-hidden', 'true');

  const label = qs('#bnb-slot-modal-title');
  if (label) modal.overlay.setAttribute('aria-labelledby', 'bnb-slot-modal-title');

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modal.overlay?.classList.contains('active')) {
      closeSlotChangeModal();
    }
    trapModalFocus(event);
  });

  renderCalendarStream();
}

window.renderCalendarStream = renderCalendarStream;
window.AirbnbCalendarState = STATE;
window.initAirbnbCalendar = initAirbnbCalendar;

export default initAirbnbCalendar;
