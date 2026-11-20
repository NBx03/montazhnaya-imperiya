/**
 * @file hero.js
 * @description Controls Hero section elements: background video autoplay assurance,
 * live CCTV REC timer, and dynamic localized date display.
 * 
 * DOM Dependencies:
 * - `#hero-bg-video`: HTML5 Video background element
 * - `#rec-timer`: Digital timecode text element (HH:MM:SS)
 * - `#hero-date`: Formatted date label (DATE / DD.MM.YYYY)
 */

/**
 * Initializes autoplay for background video with fallback interaction triggers.
 * Ensures video plays seamlessly even under restrictive mobile battery-saver policies.
 */
function initHeroVideo() {
  const heroVideo = document.getElementById('hero-bg-video');
  if (!heroVideo) return;

  const startVideo = () => {
    heroVideo.muted = true;
    const playPromise = heroVideo.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {
        // Fallback: trigger play on first user interaction if browser policy blocks autoplay
        const playOnInteract = () => {
          heroVideo.play().catch(() => {});
          ['click', 'touchstart', 'scroll'].forEach((evt) =>
            window.removeEventListener(evt, playOnInteract)
          );
        };
        ['click', 'touchstart', 'scroll'].forEach((evt) =>
          window.addEventListener(evt, playOnInteract, { passive: true, once: true })
        );
      });
    }
  };

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    startVideo();
  } else {
    window.addEventListener('load', startVideo);
  }
}

/**
 * Initializes the live REC CCTV timecode timer (increments every second from 00:00:00).
 */
function initRecTimer() {
  const recTimerEl = document.getElementById('rec-timer');
  if (!recTimerEl) return;

  let seconds = 0;
  setInterval(() => {
    seconds++;
    const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
    const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    recTimerEl.textContent = `${hrs}:${mins}:${secs}`;
  }, 1000);
}

/**
 * Populates current dynamic date in the exact Figma HUD format: DATE / DD.MM.YYYY.
 */
function initHeroDate() {
  const heroDateEl = document.getElementById('hero-date');
  if (!heroDateEl) return;

  const now = new Date();
  const d = String(now.getDate()).padStart(2, '0');
  const m = String(now.getMonth() + 1).padStart(2, '0');
  const y = now.getFullYear();
  heroDateEl.textContent = `DATE / ${d}.${m}.${y}`;
}

/**
 * Initializes all Hero section dynamic features.
 */
export function initHero() {
  initHeroVideo();
  initRecTimer();
  initHeroDate();
}
