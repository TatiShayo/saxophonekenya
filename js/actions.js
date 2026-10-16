/**
 * actions.js — Central delegated handler for every data-action control
 * --------------------------------------------------------------------------
 * WHY THIS EXISTS
 *
 * The site previously used 34 inline `onclick="..."` attributes on
 * index.html and a further 15 on rate-card.html. Inline handlers are the
 * single biggest blocker to a Content-Security-Policy: a policy without
 * `script-src 'unsafe-inline'` silently disables every one of them, so the
 * calendar, the reservation buttons and the invoice generator all stop
 * working with no visible error.
 *
 * This module replaces them with a delegated listener on `data-action`
 * attributes. Nothing is executed via eval or inline script, so a strict
 * CSP (`script-src 'self'`) is now valid.
 *
 * Markup contract
 * ---------------
 *   <button type="button" data-action="set-mode" data-mode="flexible">
 *   <button type="button" data-action="select-slot"
 *           data-slot="Evening Set (18:00 – 22:00)"
 *           data-label="Evening Reception & Cocktail"
 *           data-package="Full Wedding Day Package">
 *
 * Values are read with `dataset`, which HTML-decodes entities — so
 * `data-package="Reception &amp; Corporate Gala"` arrives as
 * "Reception & Corporate Gala" without any manual unescaping.
 */

const HANDLERS = Object.create(null);

/**
 * Register an action handler.
 * @param {string} name
 * @param {(element: HTMLElement) => void} handler
 */
export function registerAction(name, handler) {
  HANDLERS[name] = handler;
}

/**
 * Dispatch a single data-action element.
 * Exported so any module can invoke an action programmatically.
 */
export function runAction(element) {
  const action = element.dataset.action;
  const handler = HANDLERS[action];
  if (!handler) {
    console.warn(`[actions] no handler registered for "${action}"`);
    return false;
  }
  handler(element);
  return true;
}

/**
 * Install the delegated listener.
 * Uses `closest` so a click on an inner <span> still resolves to the button.
 */
export function initActions() {
  document.addEventListener('click', (event) => {
    /* Never act on a modified click — those are "open in new tab" gestures. */
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    /* Ignore middle and right clicks. */
    if (event.button !== 0) return;

    const trigger = event.target.closest('[data-action]');
    if (!trigger) return;
    if (trigger instanceof HTMLButtonElement && trigger.disabled) return;

    runAction(trigger);
  });

  /* Keyboard activation for non-button elements that carry data-action. */
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const trigger = event.target.closest('[data-action]');
    if (!trigger) return;
    if (trigger.tagName === 'BUTTON' || trigger.tagName === 'A') return; /* native */
    event.preventDefault();
    runAction(trigger);
  });
}

export default initActions;
