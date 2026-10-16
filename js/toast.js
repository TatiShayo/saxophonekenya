/**
 * toast.js — Notification system
 * --------------------------------------------------------------------------
 * SECURITY. The original implementation was:

       t.innerHTML = `<span>&bull;</span> ${msg}`;

 * and it was reached with user-controlled text from
 * generateInvoicePreview() (the client name), openPhotoViewer() and
 * selectPackageAndScroll(). That is an HTML-injection sink: a client name
 * of `<img src=x onerror=...>` would have executed.
 *
 * Every message now goes through textContent, which is a text sink, so
 * markup can never execute regardless of what the message contains.
 *
 * ACCESSIBILITY. The container is an aria-live region, so a screen-reader
 * user hears the confirmation without having to find the visual toast.
 */

import { CONFIG } from './config.js';
import { el } from './utils.js';

let container = null;

function ensureContainer() {
  if (container && document.body.contains(container)) return container;

  container = document.getElementById('toast-container');

  if (!container) {
    container = el('div', {
      id: 'toast-container',
      class: 'toast-container',
      role: 'status',
      'aria-live': 'polite',
      'aria-atomic': 'false'
    });
    document.body.appendChild(container);
  }

  return container;
}

/** Exported for tests and for other modules that need to assert emptiness. */
export function toastCount() {
  return container ? container.querySelectorAll('.toast').length : 0;
}

/**
 * showToast — display a transient notification.
 *
 * @param {string} message  Plain text. Any markup is escaped, never parsed.
 * @param {{ttl?: number}} [options]
 * @returns {{dismiss: Function, node: HTMLElement} | null}
 */
export function showToast(message, options = {}) {
  const host = ensureContainer();
  if (!host) return null;

  const ttl = options.ttl ?? CONFIG.TIMING.TOAST_MS;

  /* Built with el() so the text can only ever be a text node. */
  const dot = el('span', { class: 'toast-dot', 'aria-hidden': 'true' });
  const text = el('span', { class: 'toast-text', text: message });
  const toast = el('div', { class: 'toast' }, [dot, text]);

  host.appendChild(toast);

  let dismissed = false;

  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(120%)';
    window.setTimeout(() => toast.remove(), CONFIG.TIMING.TOAST_FADE_MS);
  };

  const timer = window.setTimeout(dismiss, ttl);

  /* Both pointer and keyboard users can dismiss immediately. */
  toast.addEventListener('click', () => {
    window.clearTimeout(timer);
    dismiss();
  });

  return { dismiss, node: toast };
}

export default showToast;
