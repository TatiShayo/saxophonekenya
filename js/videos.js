/**
 * videos.js — Live performance video theatre
 * --------------------------------------------------------------------------
 * The original markup was:
 *     <div class="cinema-video-box" onclick="togglePlayVideo(this)">
 *         <video ... controls playsinline preload="metadata">
 * That double-toggles: the native controls already pause/play, and the
 * wrapping div also fires togglePlayVideo, so a single click on the
 * controls could pause then immediately resume.
 *
 * The click target is now an explicit <button> overlay that is only shown
 * while the video is paused, and it reports its state with aria-pressed.
 * The native controls remain available and are not intercepted.
 */

import { qs, qsa, prefersReducedMotion } from './utils.js';
import { showToast } from './toast.js';

const PLAY_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';

function syncAffordance(box, video, affordance) {
  const paused = video.paused || video.ended;
  affordance.hidden = !paused;
  affordance.setAttribute('aria-pressed', String(!paused));
}

function wireCard(box) {
  const video = box.querySelector('video');
  if (!video) return;

  let affordance = box.querySelector('.cinema-play-affordance');
  if (!affordance) {
    affordance = document.createElement('button');
    affordance.type = 'button';
    affordance.className = 'cinema-play-affordance';
    affordance.setAttribute('aria-label', 'Play performance video');
    affordance.innerHTML = PLAY_SVG;
    box.appendChild(affordance);
  }

  const toggle = () => {
    if (video.paused || video.ended) {
      /* Pause the other reels so only one soundtrack plays at a time. */
      for (const other of document.querySelectorAll('.cinema-video-box video')) {
        if (other !== video && !other.paused) other.pause();
      }
      const attempt = video.play?.();
      if (attempt && typeof attempt.catch === 'function') {
        attempt.catch(() => showToast('Tap the video again to start playback'));
      }
    } else {
      video.pause();
    }
  };

  affordance.addEventListener('click', (event) => {
    event.stopPropagation();
    toggle();
  });

  /* Clicking the video surface itself is still a toggle, but only when the
     click did not land on the native control bar. */
  box.addEventListener('click', (event) => {
    if (event.target.closest('.cinema-play-affordance')) return;
    toggle();
  });

  ['play', 'pause', 'ended'].forEach((evt) => {
    video.addEventListener(evt, () => syncAffordance(box, video, affordance));
  });

  /* Videos far below the fold must not buffering-load on first paint.
     They already carry preload="metadata"; this stops the download of the
     full file until the user actually plays one. */
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        video.preload = entry.isIntersecting ? 'metadata' : 'none';
      }
    }, { rootMargin: '200px' });
    observer.observe(video);
  }

  syncAffordance(box, video, affordance);
}

export function initVideos() {
  if (prefersReducedMotion()) return; /* never autoplay anything */
  qsa('.cinema-video-box').forEach(wireCard);
}

export default initVideos;
