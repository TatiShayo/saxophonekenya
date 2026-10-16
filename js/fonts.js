/**
 * fonts.js — Non-render-blocking webfont activation
 * --------------------------------------------------------------------------
 * partials/head.html ships the Google Fonts stylesheet with media="not all",
 * which the browser fetches at low priority without blocking first paint.
 * Appending that stylesheet to the document with media="all" would apply
 * it, but this module flips the existing node's media attribute instead —
 * no second network request and no inline onload handler, so a strict
 * Content-Security-Policy (script-src without 'unsafe-inline') stays valid.
 *
 * If JavaScript is disabled, the <noscript> fallback in head.html loads the
 * stylesheet normally.
 */

const sheet = document.getElementById('webfonts');

if (sheet) {
  /* Apply as soon as the element is parsed; this module is deferred, so the
     document is already interactive and there is no flash of unstyled text. */
  sheet.media = 'all';
  sheet.addEventListener('load', () => document.documentElement.classList.add('fonts-loaded'));
}

export default true;
