/**
 * hero.js — Hero background video, audio toggle, reduced-motion handling
 * --------------------------------------------------------------------------
 * - The original <video autoplay muted> had no preload attribute, so the
 *   25.6 MB IMG_3610.MP4 began downloading immediately and became the LCP
 *   element. It now uses preload="metadata" plus an explicit poster, so the
 *   still frame paints instantly and the video only streams when needed.
 * - Autoplay is suppressed entirely under prefers-reduced-motion, matching
 *   the CSS rule in base.css that hides the video.
 * - The unmute button now carries aria-pressed so its state is announced.
 */

import { qs, prefersReducedMotion } from './utils.js';
import { showToast } from './toast.js';

const MUTE_ICON = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>';
const SOUND_ICON = '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>';

export function initHero() {
  const video = qs('#hero-video-player');
  const button = qs('#sound-btn');
  const icon = qs('#sound-icon-svg');
  const label = qs('#sound-label');

  if (!video) return;

  const reduced = prefersReducedMotion();

  /* Respect the reduced-motion preference at the JS layer too: CSS hides
     the element, but we must not also be pulling 25 MB of video down. */
  if (reduced) {
    video.pause();
    video.removeAttribute('autoplay');
    video.setAttribute('aria-hidden', 'true');
  } else {
    /* Muted autoplay is the only autoplay browsers allow. Guard the
       promise so a blocked autoplay does not surface an unhandled
       rejection in the console. */
    const attempt = video.play?.();
    if (attempt && typeof attempt.catch === 'function') {
      attempt.catch(() => { /* autoplay blocked; poster remains visible */ });
    }
  }

  if (!button) return;
  button.setAttribute('aria-pressed', 'false');

  button.addEventListener('click', () => {
    const nowMuted = !video.muted;
    video.muted = nowMuted;

    button.setAttribute('aria-pressed', String(!nowMuted));
    if (icon) icon.innerHTML = nowMuted ? MUTE_ICON : SOUND_ICON;
    if (label) label.textContent = nowMuted ? 'Unmute Performance Audio' : 'Mute Performance Audio';

    showToast(nowMuted ? 'Live saxophone audio muted' : 'Live saxophone audio unmuted');

    if (!nowMuted) {
      /* Playing audio requires a fresh user gesture; this click is it. */
      const attempt = video.play?.();
      if (attempt && typeof attempt.catch === 'function') attempt.catch(() => {});
    }
  });
}

export default initHero;
