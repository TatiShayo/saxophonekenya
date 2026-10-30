/**
 * utils.js — DOM, date, validation and safe-string helpers
 * --------------------------------------------------------------------------
 * Nothing here touches the DOM at import time, so this module is safe to
 * import from anywhere. Every helper that handles user-supplied text goes
 * through textContent rather than innerHTML — see safeSetText().
 */

import { CONFIG } from './config.js';

   DOM helpers
   -------------------------------------------------------------------------- */

/** document.querySelector shorthand that never throws. */
export function qs(selector, scope = document) {
  return scope.querySelector(selector);
}

/** document.querySelectorAll shorthand that always returns an array. */
export function qsa(selector, scope = document) {
  return Array.from(scope.querySelectorAll(selector));
}

/** Element factory. All attribute values are set via setAttribute, so a
 *  value containing quotes or angle brackets cannot break out of the tag. */
export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === 'class') node.className = value;
    else if (key === 'text') node.textContent = value;
    else if (key === 'dataset') Object.assign(node.dataset, value);
    else node.setAttribute(key, value === true ? '' : String(value));
  }
  for (const child of [].concat(children)) {
    if (child === null || child === undefined) continue;
    node.append(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return node;
}

/**
 * safeSetText — the ONLY sanctioned way to put text into a node.
 *
 * The original site interpolated user-derived strings into innerHTML in
 * four places (showToast, generateInvoicePreview, openPhotoViewer and
 * king-sax.html's toast). This helper makes that class of bug impossible:
 * textContent is a text sink, so markup can never execute.
 */
export function safeSetText(node, text) {
  if (!node) return;
  node.textContent = String(text ?? '');
}

   Date helpers
   -------------------------------------------------------------------------- */

export const MONTH_NAMES = Object.freeze([
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]);

export const DAY_NAMES = Object.freeze([
  'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
]);

/** YYYY-MM-DD in *local* time.
 *
 *  toISOString() returns a UTC string. For a visitor in East Africa
 *  (UTC+3) any local time between 00:00 and 03:00 would format as the
 *  previous day, which let a past date be booked. formatISODate() is the
 *  replacement used everywhere. */
export function formatISODate(date) {
  if (!date) return '';
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

/** Today at local midnight — the comparison baseline for "past". */
export function startOfToday() {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

export function daysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

/** Monday-first column offset: Mon=0 … Sun=6. */
export function mondayFirstIndex(year, month, day = 1) {
  return (new Date(year, month, day).getDay() + 6) % 7;
}

export function isSameDay(a, b) {
  if (!a || !b) return false;
  return a.getFullYear() === b.getFullYear() &&
         a.getMonth() === b.getMonth() &&
         a.getDate() === b.getDate();
}

/** "Thursday, 15 October 2026" */
export function formatReadableDate(date) {
  if (!date) return '';
  return `${DAY_NAMES[date.getDay()]}, ${date.getDate()} ${MONTH_NAMES[date.getMonth()]} ${date.getFullYear()}`;
}

/** "Oct 8 – 10, 2026" / "Oct 8 – Nov 2, 2026" */
export function formatRangeDisplay(start, end) {
  if (!start) return 'Select performance dates';
  const sMonth = MONTH_NAMES[start.getMonth()].slice(0, 3);
  if (!end || isSameDay(start, end)) {
    return `${sMonth} ${start.getDate()}, ${start.getFullYear()}`;
  }
  const eMonth = MONTH_NAMES[end.getMonth()].slice(0, 3);
  if (start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()) {
    return `${sMonth} ${start.getDate()} – ${end.getDate()}, ${start.getFullYear()}`;
  }
  return `${sMonth} ${start.getDate()} – ${eMonth} ${end.getDate()}, ${end.getFullYear()}`;
}

   Validation
   -------------------------------------------------------------------------- */

/** Kenyan and international formats both accepted.
 *  Accepts: +254712345678, 0712345678, 0712 345 678, 0123-456-789. */
export function isValidPhone(raw) {
  if (!raw) return false;
  const digits = raw.replace(/[\s()\-.]/g, '');
  return /^(?:\+?\d{1,3})?\d{6,14}$/.test(digits);
}

export function isValidEmail(raw) {
  if (!raw) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(raw.trim());
}

/** Guard against a date earlier than today. */
export function isFutureDate(value) {
  if (!value) return false;
  const parsed = new Date(`${value}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return false;
  return parsed >= startOfToday();
}

/**
 * markFieldError — toggles .has-error on the field wrapper and writes the
 * message with textContent. Replaces the original pattern where validation
 * feedback was a non-existent function.
 */
export function markFieldError(input, message) {
  const field = input.closest('.form-field');
  if (!field) return;
  field.classList.add('has-error');
  const errorNode = field.querySelector('.form-error');
  if (errorNode) errorNode.textContent = message;
  input.setAttribute('aria-invalid', 'true');
}

export function clearFieldError(input) {
  const field = input.closest('.form-field');
  if (!field) return;
  field.classList.remove('has-error');
  input.removeAttribute('aria-invalid');
}

   Misc
   -------------------------------------------------------------------------- */

/**
 * openExternal — the only sanctioned way to open a new window.
 *
 * window.open(url, '_blank') without noopener hands the opened document a
 * live `window.opener` reference, which is the reverse-tabnabbing vector.
 * Every outbound link on the site now goes through here.
 */
export function openExternal(url) {
  const win = window.open(url, '_blank', 'noopener,noreferrer');
  if (win) win.opener = null;
  return win;
}

/** Build an absolute URL for og:image / canonical tags. */
export function absoluteUrl(path) {
  if (!path) return '';
  if (/^https?:\/\//i.test(path)) return path;
  return `${CONFIG.SITE_ORIGIN}/${String(path).replace(/^\/+/, '')}`;
}

/** Prefers-reduced-motion check, so JS honours it too, not just CSS. */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/** requestAnimationFrame-throttled scroll/resize listener. */
export function onThrottledScroll(handler) {
  let queued = false;
  window.addEventListener('scroll', () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; handler(); });
  }, { passive: true });
}
